"""Validação em duas camadas (RF-03 a RF-06):
1) sintática — JSON Schema 2020-12 do contrato;
2) semântica — regras que o schema não expressa (geometria, agregado, consistência espacial)."""
from __future__ import annotations
import json, pathlib
from dataclasses import dataclass, field, asdict
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from shapely.geometry import shape, box as shp_box
from shapely.validation import explain_validity

SCHEMAS = pathlib.Path(__file__).resolve().parents[1] / "schemas" / "json"
_TIPO_ARQ = {"Edificacao": "edificacao", "Via": "via", "PontoDeInteresse": "ponto-de-interesse",
             "AreaVerde": "area-verde"}
TOL = 0.01          # m, tolerância numérica
TOL_PORTARIA = 5.0  # m, distância máxima da portaria ao perímetro

def _registry():
    res = [(json.loads(p.read_text("utf-8"))["$id"], Resource.from_contents(json.loads(p.read_text("utf-8"))))
           for p in SCHEMAS.glob("*.schema.json")]
    return Registry().with_resources(res)
_REG = _registry()
def _validador(nome):
    s = json.loads((SCHEMAS / f"{nome}.schema.json").read_text("utf-8"))
    return Draft202012Validator(s, registry=_REG)
_VAL = {k: _validador(v) for k, v in _TIPO_ARQ.items()}
_VAL_MODELO = _validador("modelo-do-campus")

@dataclass
class Erro:
    codigo: str
    regra: str
    local: str      # JSON Pointer
    mensagem: str

@dataclass
class RelatorioDeValidacao:
    valido: bool = True
    erros: list = field(default_factory=list)
    def add(self, codigo, regra, local, mensagem):
        self.valido = False; self.erros.append(Erro(codigo, regra, local, mensagem))
    def para_dict(self): return {"valido": self.valido, "erros": [asdict(e) for e in self.erros]}

def _regra_schema(err) -> str:
    """Associa um erro de schema à invariante do catálogo (rastreabilidade RNF-03)."""
    path = list(err.absolute_path)
    ult = path[-1] if path else None
    if err.validator == "required" and "'categoria'" in err.message: return "INV-07"
    if err.validator == "required" and "'endereco'" in err.message: return "INV-14"
    if ult == "crs": return "INV-10"
    if ult in ("categoria", "categoriaUso", "classe", "revestimento", "cobertura", "situacao"): return "INV-09"
    if ult == "id" or (path and "id" in path): return "INV-01"
    return "SCHEMA"

def _ptr(path): return "/" + "/".join(str(p) for p in path) if path else "/"

def _validar_schema(v, doc, rel, prefixo=()):
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        rel.add("G1-SCH-001", _regra_schema(e), _ptr(list(prefixo) + list(e.absolute_path)), e.message)

def _poligono_ok(g, rel, local):
    anel = g["coordinates"][0]
    if anel[0] != anel[-1]:
        rel.add("G1-GEO-003", "INV-03", local, "anel exterior não está fechado (primeiro ponto ≠ último)"); return None
    p = shape(g)
    if not p.is_valid or p.area <= TOL:
        rel.add("G1-GEO-003", "INV-03", local, f"polígono inválido: {explain_validity(p)}"); return None
    return p

def _semantica_objeto(d, rel, base=""):
    if d["geometria"]["type"] == "Polygon":
        poly = _poligono_ok(d["geometria"], rel, base + "/geometria")
    if d["tipo"] == "Edificacao":
        end = d.get("endereco")
        if d["localizacao"] == "externa" and end and str(d["numeroMapa"]) != end["numero"]:
            rel.add("G1-AGR-015", "INV-15", base + "/numeroMapa",
                    f"edificação externa: número do mapa ({d['numeroMapa']}) difere do número do endereço ({end['numero']})")
        nums = {}
        for i, p in enumerate(d.get("pavimentos", [])):
            loc = f"{base}/pavimentos/{i}"
            if p["numero"] in nums:
                rel.add("G1-AGR-005", "INV-05", loc + "/numero",
                        f"pavimento {p['numero']} repetido na edificação {d['numeroMapa']}")
            nums[p["numero"]] = i
            pg = _poligono_ok(p["geometria"], rel, loc + "/geometria")
            if pg is not None and poly is not None and not poly.buffer(TOL).covers(pg):
                rel.add("G1-AGR-004", "INV-04", loc + "/geometria",
                        f"pavimento {p['numero']} extrapola a projeção da edificação {d['numeroMapa']}")

def validar(doc: dict) -> RelatorioDeValidacao:
    """Valida um objeto urbano isolado (regras do próprio agregado)."""
    rel = RelatorioDeValidacao()
    v = _VAL.get(doc.get("tipo"))
    if v is None:
        rel.add("G1-SCH-001", "SCHEMA", "/tipo", f"tipo desconhecido: {doc.get('tipo')}"); return rel
    _validar_schema(v, doc, rel)
    if rel.valido: _semantica_objeto(doc, rel)
    return rel

def validar_modelo(modelo: dict) -> RelatorioDeValidacao:
    """Valida um instantâneo do campus: agregados + consistência espacial entre eles."""
    rel = RelatorioDeValidacao()
    _validar_schema(_VAL_MODELO, modelo, rel)
    if not rel.valido: return rel
    objs = modelo["objetos"]
    for i, o in enumerate(objs): _semantica_objeto(o, rel, f"/objetos/{i}")
    if not rel.valido: return rel
    perim = shape(modelo["campus"]["perimetro"]); adi = shp_box(*modelo["campus"]["areaDeInteresse"])
    ids, nums = {}, {}
    geos = [shape(o["geometria"]) for o in objs]
    for i, (o, g) in enumerate(zip(objs, geos)):
        loc = f"/objetos/{i}"
        if o["id"] in ids: rel.add("G1-ESP-001", "INV-01", loc + "/id", f"identificador duplicado: {o['id']}")
        ids[o["id"]] = i
        if o["tipo"] == "Edificacao":
            # INV-11: numeração do mapa é única entre internas; externas são numeradas pelo endereço
            chave = (("interna", o["numeroMapa"]) if o["localizacao"] == "interna"
                     else ("externa", o["endereco"]["logradouro"], o["endereco"]["numero"]))
            if chave in nums:
                rel.add("G1-ESP-011", "INV-11", loc + "/numeroMapa",
                        f"número do mapa {o['numeroMapa']} já usado por {objs[nums[chave]]['id']}")
            nums[chave] = i
            dentro = perim.buffer(1.0).covers(g)
            if o["localizacao"] == "interna" and not dentro:
                rel.add("G1-ESP-012", "INV-12", loc + "/geometria", "edificação interna fora do perímetro do campus")
            if o["localizacao"] == "externa" and perim.intersection(g).area > TOL:
                rel.add("G1-ESP-012", "INV-12", loc + "/geometria", "edificação externa sobreposta ao perímetro do campus")
        if not adi.covers(g):
            rel.add("G1-ESP-002", "INV-02", loc + "/geometria", "geometria fora da área de interesse do campus")
        if o["tipo"] == "PontoDeInteresse" and o["categoria"] == "portaria":
            dist = perim.exterior.distance(g)
            if dist > TOL_PORTARIA:
                rel.add("G1-ESP-013", "INV-13", loc + "/geometria",
                        f"portaria a {dist:.1f} m do perímetro (máx. {TOL_PORTARIA} m)")
    edfs = [(j, g) for j, (o, g) in enumerate(zip(objs, geos)) if o["tipo"] == "Edificacao"]
    for i, (o, g) in enumerate(zip(objs, geos)):
        for j, ge in edfs:
            if o["tipo"] == "Via" and g.intersection(ge.buffer(-TOL)).length > TOL:
                rel.add("G1-ESP-006", "INV-06", f"/objetos/{i}/geometria",
                        f"via '{o['nome']}' atravessa a edificação {objs[j]['numeroMapa']}")
            if o["tipo"] == "AreaVerde" and g.intersection(ge).area > TOL:
                rel.add("G1-ESP-008", "INV-08", f"/objetos/{i}/geometria",
                        f"área verde '{o['nome']}' sobrepõe a edificação {objs[j]['numeroMapa']}")
    return rel
