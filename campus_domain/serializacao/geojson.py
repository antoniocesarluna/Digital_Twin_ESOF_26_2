"""Exportação e importação GeoJSON (RFC 7946) — RF12 (exportação em padrões abertos) e RF10
(o desenho feito no Leaflet chega em WGS 84 e é convertido para o CRS canônico antes da validação).
GeoJSON exige longitude/latitude em WGS 84 (EPSG:4326); o contrato usa EPSG:31983 (ADR-003)."""
import copy

from pyproj import Transformer

from ..auditoria import auditar_transformacao

CRS = "EPSG:31983"
_PARA_WGS = Transformer.from_crs(CRS, "EPSG:4326", always_xy=True)
_DE_WGS = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
CASAS_WGS, CASAS_UTM = 8, 2   # 1e-8 grau ≈ 1 mm; contrato em centímetros

def _conv(coords, tr, casas):
    if isinstance(coords[0], (int, float)):
        x, y = tr.transform(coords[0], coords[1]); return [round(x, casas), round(y, casas)]
    return [_conv(c, tr, casas) for c in coords]

def _geo(g, tr, casas): return {"type": g["type"], "coordinates": _conv(g["coordinates"], tr, casas)}

@auditar_transformacao("contrato EPSG:31983", "GeoJSON EPSG:4326")
def para_geojson(docs) -> dict:
    """Objetos do domínio (lista ou modelo do campus) -> FeatureCollection em WGS 84, pronta para L.geoJSON()."""
    objs = docs["objetos"] if isinstance(docs, dict) and "objetos" in docs else (docs if isinstance(docs, list) else [docs])
    feats = []
    for o in objs:
        props = {k: copy.deepcopy(v) for k, v in o.items() if k not in ("id", "crs", "geometria")}
        for p in props.get("pavimentos", []):
            p["geometria"] = _geo(p["geometria"], _PARA_WGS, CASAS_WGS)
        feats.append({"type": "Feature", "id": o["id"], "geometry": _geo(o["geometria"], _PARA_WGS, CASAS_WGS), "properties": props})
    return {"type": "FeatureCollection", "features": feats}

@auditar_transformacao("GeoJSON EPSG:4326", "contrato EPSG:31983")
def de_geojson(fc: dict) -> list:
    """FeatureCollection (ou Feature) em WGS 84 -> documentos do contrato em EPSG:31983, prontos para validar()."""
    feats = fc["features"] if fc.get("type") == "FeatureCollection" else [fc]
    out = []
    for f in feats:
        props = copy.deepcopy(f.get("properties") or {})
        for p in props.get("pavimentos", []):
            p["geometria"] = _geo(p["geometria"], _DE_WGS, CASAS_UTM)
        doc = {"tipo": props.pop("tipo"), "id": f["id"], "crs": CRS, **props,
               "geometria": _geo(f["geometry"], _DE_WGS, CASAS_UTM)}
        out.append(doc)
    return out
