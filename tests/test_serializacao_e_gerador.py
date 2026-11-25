import xml.etree.ElementTree as ET
import pytest
from pyld import jsonld
from campus_domain import de_dict, para_dict, para_gml, para_jsonld, gerar_campus, validar_modelo
from campus_domain.serializacao.gml import NS
from conftest import carregar

@pytest.mark.parametrize("i", range(12))
def test_round_trip_documento_dominio_documento(modelo, i):
    original = {k: v for k, v in modelo["objetos"][i].items() if k != "metadados"}
    assert para_dict(de_dict(original)) == original

def test_gml_bem_formado_com_pavimentos(modelo):
    e41 = de_dict(next(o for o in modelo["objetos"] if o["id"].endswith(":41")))
    raiz = ET.fromstring(para_gml(e41).split("?>", 1)[1])
    assert len(raiz.findall(".//bldg:Storey", NS)) == 2
    assert raiz.find(".//gml:posList", NS).text.count(" ") == 9  # 5 posições x 2 coords - 1

def test_jsonld_expande_com_contexto_publicado(modelo):
    ctx = carregar("schemas/jsonld/context.jsonld")
    doc = para_jsonld(modelo["objetos"][0], contexto=ctx["@context"])
    exp = jsonld.expand(doc)
    assert exp[0]["@type"] == ["urn:upm:campus-hig:vocab#Edificacao"]
    assert "https://schema.org/name" in exp[0]

@pytest.mark.parametrize("semente", range(25))
def test_propriedade_campus_gerado_e_sempre_valido(modelo, semente):
    m = gerar_campus(modelo, n=15, semente=semente)
    assert validar_modelo(m).valido

def test_numero_40_interno_e_externo_coexistem(modelo):
    quarenta = [o for o in modelo["objetos"] if o.get("numeroMapa") == 40]
    assert {o["localizacao"] for o in quarenta} == {"interna", "externa"} and validar_modelo(modelo).valido

def test_gerador_reproduzivel(modelo):
    assert gerar_campus(modelo, semente=7) == gerar_campus(modelo, semente=7)

@pytest.mark.parametrize("regra", ["INV-08", "INV-11"])
def test_gerador_modo_invalido_controlado(modelo, regra):
    r = validar_modelo(gerar_campus(modelo, n=5, semente=3, violar=regra))
    assert not r.valido and {e.regra for e in r.erros} == {regra}
