"""RF12 (exportação OGC/GeoJSON) e RF10 (desenho do Leaflet em WGS 84 -> contrato)."""
import xml.etree.ElementTree as ET

from campus_domain import de_dict, de_geojson, para_geojson, para_gml, validar, validar_modelo
from campus_domain.serializacao.gml import NS


def _sem_meta(o): return {k: v for k, v in o.items() if k != "metadados"}

def test_geojson_em_wgs84_lon_lat(modelo):
    fc = para_geojson(modelo)
    assert fc["type"] == "FeatureCollection" and len(fc["features"]) == len(modelo["objetos"])
    lon, lat = fc["features"][0]["geometry"]["coordinates"][0][0]
    assert -46.66 < lon < -46.64 and -23.56 < lat < -23.54   # Higienópolis

def test_geojson_ida_e_volta_preserva_o_contrato(modelo):
    volta = de_geojson(para_geojson(modelo))
    assert volta == modelo["objetos"]

def test_desenho_do_leaflet_vira_objeto_valido(modelo):
    """Simula o formulário do G5: Feature desenhada em WGS 84 -> G3 converte e valida com o G1."""
    feat = para_geojson(modelo["objetos"][0])["features"][0]
    doc = de_geojson(feat)[0]
    assert doc["crs"] == "EPSG:31983" and validar(doc).valido

def test_modelo_reimportado_continua_consistente(modelo):
    m = dict(modelo); m["objetos"] = de_geojson(para_geojson(modelo))
    assert validar_modelo(m).valido

def test_citygml_exporta_os_quatro_tipos(modelo):
    objs = [de_dict(_sem_meta(o)) for o in modelo["objetos"]]
    raiz = ET.fromstring(para_gml(objs).split("?>", 1)[1])
    contagem = {t: len(raiz.findall(f".//{t}", NS)) for t in ("bldg:Building", "tran:Road", "veg:PlantCover", "gen:GenericOccupiedSpace")}
    esperado = {"bldg:Building": 6, "tran:Road": 2, "veg:PlantCover": 1, "gen:GenericOccupiedSpace": 3}
    assert contagem == esperado

def test_citygml_ids_unicos(modelo):
    objs = [de_dict(_sem_meta(o)) for o in modelo["objetos"]]
    ids = [e.get(f"{{{NS['gml']}}}id") for e in ET.fromstring(para_gml(objs).split("?>", 1)[1]).iter() if e.get(f"{{{NS['gml']}}}id")]
    assert len(ids) == len(set(ids))
