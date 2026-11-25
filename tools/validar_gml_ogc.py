"""Conformidade do CityGML exportado com os XSD oficiais da OGC (job conformidade-gml do CI).
Requer rede para schemas.opengis.net e lxml. uso: python tools/validar_gml_ogc.py"""
import json
import pathlib
import sys

from lxml import etree

RAIZ = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(RAIZ))
from campus_domain import de_dict, para_gml

OGC = "https://schemas.opengis.net/citygml/"
MODULOS = {"http://www.opengis.net/citygml/building/3.0": OGC + "building/3.0/building.xsd",
           "http://www.opengis.net/citygml/transportation/3.0": OGC + "transportation/3.0/transportation.xsd",
           "http://www.opengis.net/citygml/vegetation/3.0": OGC + "vegetation/3.0/vegetation.xsd",
           "http://www.opengis.net/citygml/generics/3.0": OGC + "generics/3.0/generics.xsd"}
def main():
    imports = "".join(f'<xs:import namespace="{ns}" schemaLocation="{url}"/>' for ns, url in MODULOS.items())
    xsd = f'<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">{imports}</xs:schema>'
    parser = etree.XMLParser(no_network=False)
    try:
        schema = etree.XMLSchema(etree.fromstring(xsd.encode(), parser))
    except (etree.XMLSchemaParseError, OSError) as e:
        print(f"schemas OGC indisponíveis: {e}"); sys.exit(2)
    modelo = json.loads((RAIZ / "examples/valid/modelo-campus-higienopolis.json").read_text("utf-8"))
    gml = para_gml([de_dict({k: v for k, v in o.items() if k != "metadados"}) for o in modelo["objetos"]])
    doc = etree.fromstring(gml.split("?>", 1)[1].encode())
    if schema.validate(doc):
        print(f"CityGML conforme ({len(modelo['objetos'])} objetos)"); return
    for e in schema.error_log: print(f"linha {e.line}: {e.message}")
    sys.exit(1)
if __name__ == "__main__":
    main()
