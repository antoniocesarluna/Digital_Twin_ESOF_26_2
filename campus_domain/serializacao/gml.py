"""Serialização domínio -> CityGML 3.0 / GML 3.2 (RF-07, exportação OGC).
O contrato do G1 é somente JSON Schema (ADR-009); o GML é um formato de exportação.
Atributos do domínio sem classe CityGML vão como gen:genericAttribute (sem ADE)."""
import xml.etree.ElementTree as ET

from ..auditoria import registrar
from ..dominio import AreaVerde, Edificacao, PontoDeInteresse, Via

NS = {"core": "http://www.opengis.net/citygml/3.0", "bldg": "http://www.opengis.net/citygml/building/3.0",
      "tran": "http://www.opengis.net/citygml/transportation/3.0", "veg": "http://www.opengis.net/citygml/vegetation/3.0",
      "gen": "http://www.opengis.net/citygml/generics/3.0", "gml": "http://www.opengis.net/gml/3.2"}
for k, v in NS.items(): ET.register_namespace(k, v)
SRS = "http://www.opengis.net/def/crs/EPSG/0/31983"
q = lambda p, n: f"{{{NS[p]}}}{n}"

def _gid(iri): return iri.split(":", 3)[-1].replace(":", "-").upper()

def _poly(parent, g, gid):
    ms = ET.SubElement(parent, q("gml", "MultiSurface"), {q("gml", "id"): gid + "-MS", "srsName": SRS})
    pol = ET.SubElement(ET.SubElement(ms, q("gml", "surfaceMember")), q("gml", "Polygon"))
    lr = ET.SubElement(ET.SubElement(pol, q("gml", "exterior")), q("gml", "LinearRing"))
    ET.SubElement(lr, q("gml", "posList")).text = " ".join(f"{x} {y}" for x, y in g.coordenadas[0])

def _attr(parent, nome, valor, tipo="StringAttribute"):
    a = ET.SubElement(ET.SubElement(parent, q("core", "genericAttribute")), q("gen", tipo))
    ET.SubElement(a, q("gen", "name")).text = nome
    ET.SubElement(a, q("gen", "value")).text = str(valor)

def _linha(parent, g, gid):
    mc = ET.SubElement(parent, q("gml", "MultiCurve"), {q("gml", "id"): gid + "-MC", "srsName": SRS})
    ls = ET.SubElement(ET.SubElement(mc, q("gml", "curveMember")), q("gml", "LineString"))
    ET.SubElement(ls, q("gml", "posList")).text = " ".join(f"{x} {y}" for x, y in g.coordenadas)

def _ponto(parent, g, gid):
    pt = ET.SubElement(parent, q("gml", "Point"), {q("gml", "id"): gid + "-PT", "srsName": SRS})
    ET.SubElement(pt, q("gml", "pos")).text = f"{g.coordenadas[0]} {g.coordenadas[1]}"

def _cabecalho(parent, o, gid):
    ET.SubElement(parent, q("gml", "identifier"), {"codeSpace": "urn:upm:campus-hig"}).text = o.id.valor
    ET.SubElement(parent, q("gml", "name")).text = o.nome

def _edificacao(cm, e):
    gid = _gid(e.id.valor)
    b = ET.SubElement(ET.SubElement(cm, q("core", "cityObjectMember")), q("bldg", "Building"), {q("gml", "id"): gid})
    _cabecalho(b, e, gid)
    _attr(b, "numeroMapa", e.numero_mapa.valor, "IntAttribute")
    _attr(b, "localizacao", e.localizacao); _attr(b, "categoriaUso", e.categoria_uso)
    if e.homenageado: _attr(b, "homenageado", e.homenageado)
    for u in e.unidades_ocupantes: _attr(b, "unidadeOcupante", u)
    _poly(ET.SubElement(b, q("core", "lod0MultiSurface")), e.geometria, gid)
    for p in e.pavimentos:
        pid = _gid(p.id.valor)
        s = ET.SubElement(ET.SubElement(b, q("bldg", "buildingSubdivision")), q("bldg", "Storey"), {q("gml", "id"): pid})
        ET.SubElement(s, q("gml", "name")).text = p.nome
        _attr(s, "numero", p.numero, "IntAttribute")
        for u in p.unidades_ocupantes: _attr(s, "unidadeOcupante", u)

def _via(cm, v):
    gid = _gid(v.id.valor)
    r = ET.SubElement(ET.SubElement(cm, q("core", "cityObjectMember")), q("tran", "Road"), {q("gml", "id"): gid})
    _cabecalho(r, v, gid); _attr(r, "classeVia", v.classe); _attr(r, "revestimento", v.revestimento)
    _linha(ET.SubElement(r, q("core", "lod0MultiCurve")), v.geometria, gid)

def _area_verde(cm, a):
    gid = _gid(a.id.valor)
    pc = ET.SubElement(ET.SubElement(cm, q("core", "cityObjectMember")), q("veg", "PlantCover"), {q("gml", "id"): gid})
    _cabecalho(pc, a, gid); _attr(pc, "coberturaVegetal", a.cobertura)
    _poly(ET.SubElement(pc, q("core", "lod0MultiSurface")), a.geometria, gid)

def _poi(cm, p):
    gid = _gid(p.id.valor)
    g = ET.SubElement(ET.SubElement(cm, q("core", "cityObjectMember")), q("gen", "GenericOccupiedSpace"), {q("gml", "id"): gid})
    _cabecalho(g, p, gid); _attr(g, "categoria", p.categoria)
    if p.numero_portaria is not None: _attr(g, "numeroPortaria", p.numero_portaria, "IntAttribute")
    if p.edificacao_ref: _attr(g, "situadoEm", p.edificacao_ref.valor)
    _ponto(ET.SubElement(g, q("core", "lod0Point")), p.geometria, gid)

_SERIAL = {Edificacao: _edificacao, Via: _via, AreaVerde: _area_verde, PontoDeInteresse: _poi}

def para_gml(objetos) -> str:
    """Exporta objetos de domínio (um ou vários, de qualquer tipo) como core:CityModel CityGML 3.0."""
    if not isinstance(objetos, (list, tuple)): objetos = [objetos]
    cm = ET.Element(q("core", "CityModel"))
    for o in objetos:
        _SERIAL[type(o)](cm, o)
    ET.indent(cm)
    registrar("transformacao", origem="domínio", destino="CityGML 3.0", funcao="para_gml", quantidade=len(objetos))
    return ET.tostring(cm, encoding="unicode", xml_declaration=True)
