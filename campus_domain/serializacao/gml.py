"""Serialização domínio -> CityGML 3.0 / GML 3.2 (RF-07).
v0.1.0: atributos do domínio como atributos genéricos CityGML; a estrutura deve ser
confirmada pelo job de conformidade contra os XSD oficiais da OGC (Sprint 3)."""
import xml.etree.ElementTree as ET
from ..dominio import Edificacao

NS = {"core": "http://www.opengis.net/citygml/3.0", "bldg": "http://www.opengis.net/citygml/building/3.0",
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

def para_gml(edificacoes) -> str:
    if isinstance(edificacoes, Edificacao): edificacoes = [edificacoes]
    cm = ET.Element(q("core", "CityModel"))
    for e in edificacoes:
        gid = _gid(e.id.valor)
        b = ET.SubElement(ET.SubElement(cm, q("core", "cityObjectMember")), q("bldg", "Building"), {q("gml", "id"): gid})
        ET.SubElement(b, q("gml", "identifier"), {"codeSpace": "urn:upm:campus-hig"}).text = e.id.valor
        ET.SubElement(b, q("gml", "name")).text = e.nome
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
    ET.indent(cm)
    return ET.tostring(cm, encoding="unicode", xml_declaration=True)
