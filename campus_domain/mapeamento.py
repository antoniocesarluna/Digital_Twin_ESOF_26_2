"""Tradução documento (dict conforme o contrato) <-> objetos de domínio."""
from .dominio import AreaVerde, Edificacao, Endereco, Geometria, Identificador, NumeroMapa, Pavimento, PontoDeInteresse, Via


def _tup(c):
    return tuple(_tup(x) for x in c) if isinstance(c, list) else c
def _lst(c):
    return [_lst(x) for x in c] if isinstance(c, tuple) else c
def _geo(d, crs): return Geometria(d["type"], _tup(d["coordinates"]), crs)
def _end(d): return Endereco(**d) if d else None

def de_dict(d: dict):
    t, crs = d["tipo"], d["crs"]
    if t == "Edificacao":
        e = Edificacao.criar(id=Identificador(d["id"]), numero_mapa=NumeroMapa(d["numeroMapa"]), nome=d["nome"],
            localizacao=d["localizacao"], categoria_uso=d["categoriaUso"], situacao=d["situacao"],
            geometria=_geo(d["geometria"], crs), homenageado=d.get("homenageado"),
            endereco=_end(d.get("endereco")), unidades_ocupantes=tuple(d.get("unidadesOcupantes", ())))
        for p in d.get("pavimentos", []):
            e.adicionar_pavimento(Pavimento(Identificador(p["id"]), p["numero"], p["nome"], _geo(p["geometria"], crs),
                                            tuple(p.get("unidadesOcupantes", ()))))
        return e
    if t == "Via":
        return Via(Identificador(d["id"]), d["nome"], d["classe"], _geo(d["geometria"], crs), d.get("revestimento", "nao-informado"))
    if t == "PontoDeInteresse":
        ref = d.get("edificacaoRef")
        return PontoDeInteresse.criar(id=Identificador(d["id"]), nome=d["nome"], categoria=d["categoria"],
            geometria=_geo(d["geometria"], crs), numero_portaria=d.get("numeroPortaria"),
            endereco=_end(d.get("endereco")), edificacao_ref=Identificador(ref) if ref else None)
    if t == "AreaVerde":
        return AreaVerde(Identificador(d["id"]), d["nome"], d["cobertura"], _geo(d["geometria"], crs))
    raise ValueError(f"tipo desconhecido: {t}")

def _g(g): return {"type": g.tipo, "coordinates": _lst(g.coordenadas)}
def _e(e): return None if e is None else {"logradouro": e.logradouro, "numero": e.numero, "municipio": e.municipio, "uf": e.uf}
def _clean(d): return {k: v for k, v in d.items() if v not in (None, (), [])}

def para_dict(o) -> dict:
    if isinstance(o, Edificacao):
        return _clean({"tipo": "Edificacao", "id": o.id.valor, "crs": o.geometria.crs, "numeroMapa": o.numero_mapa.valor,
            "nome": o.nome, "homenageado": o.homenageado, "localizacao": o.localizacao, "categoriaUso": o.categoria_uso,
            "unidadesOcupantes": list(o.unidades_ocupantes), "endereco": _e(o.endereco), "situacao": o.situacao,
            "geometria": _g(o.geometria), "pavimentos": [_clean({"id": p.id.valor, "numero": p.numero, "nome": p.nome,
                "geometria": _g(p.geometria), "unidadesOcupantes": list(p.unidades_ocupantes)}) for p in o.pavimentos]})
    if isinstance(o, Via):
        return {"tipo": "Via", "id": o.id.valor, "crs": o.geometria.crs, "nome": o.nome, "classe": o.classe,
                "revestimento": o.revestimento, "geometria": _g(o.geometria)}
    if isinstance(o, PontoDeInteresse):
        return _clean({"tipo": "PontoDeInteresse", "id": o.id.valor, "crs": o.geometria.crs, "nome": o.nome,
            "categoria": o.categoria, "numeroPortaria": o.numero_portaria, "endereco": _e(o.endereco),
            "edificacaoRef": o.edificacao_ref.valor if o.edificacao_ref else None, "geometria": _g(o.geometria)})
    if isinstance(o, AreaVerde):
        return {"tipo": "AreaVerde", "id": o.id.valor, "crs": o.geometria.crs, "nome": o.nome,
                "cobertura": o.cobertura, "geometria": _g(o.geometria)}
    raise TypeError(type(o))
