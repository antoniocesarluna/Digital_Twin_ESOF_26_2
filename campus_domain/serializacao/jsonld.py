"""Serialização documento -> JSON-LD (RF-09). O @context publicado liga cada termo
da linguagem ubíqua a um IRI (CityGML, GeoSPARQL, schema.org ou vocabulário do campus)."""
import copy
CONTEXTO = "https://gemeo-campus.example/schemas/0.1.0/context.jsonld"
def para_jsonld(doc: dict, contexto=CONTEXTO) -> dict:
    d = copy.deepcopy(doc); d.pop("metadados", None)
    return {"@context": contexto, **d}
