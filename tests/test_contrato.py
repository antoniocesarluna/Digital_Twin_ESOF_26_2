"""Harness do contrato: schemas válidos, vocabulários sincronizados, exemplos coerentes."""
import json, pathlib, pytest
from jsonschema import Draft202012Validator
from lxml import etree
from campus_domain import validar, validar_modelo
from conftest import RAIZ, carregar

SCHEMAS = sorted((RAIZ / "schemas/json").glob("*.schema.json"))
VALIDOS = sorted((RAIZ / "examples/valid").glob("*.json"))
INVALIDOS = sorted((RAIZ / "examples/invalid").glob("*.json"))

@pytest.mark.parametrize("arq", SCHEMAS, ids=lambda p: p.name)
def test_schema_conforme_metaschema_2020_12(arq):
    Draft202012Validator.check_schema(json.loads(arq.read_text("utf-8")))

def test_xsd_do_perfil_compila():
    etree.XMLSchema(etree.parse(str(RAIZ / "schemas/xsd/campus-ade.xsd")))

@pytest.mark.parametrize("vocab,campo,arq", [
    ("categoriaUso", "categoriaUso", "edificacao"), ("categoriaPontoDeInteresse", "categoria", "ponto-de-interesse"),
    ("classeVia", "classe", "via"), ("coberturaVegetal", "cobertura", "area-verde")])
def test_vocabulario_sincronizado_com_schema(vocab, campo, arq):
    termos = [t["codigo"] for t in carregar(f"schemas/vocab/{vocab}.json")["termos"]]
    assert carregar(f"schemas/json/{arq}.schema.json")["properties"][campo]["enum"] == termos

def test_contexto_jsonld_cobre_termos_dos_schemas():
    ctx = carregar("schemas/jsonld/context.jsonld")["@context"]
    for arq in ("edificacao", "via", "ponto-de-interesse", "area-verde"):
        props = carregar(f"schemas/json/{arq}.schema.json")["properties"]
        faltando = [p for p in props if p not in ctx]
        assert not faltando, f"{arq}: termos sem IRI no @context: {faltando}"

@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_exemplo_valido_passa(arq):
    d = carregar(arq)
    r = validar_modelo(d) if "objetos" in d else validar(d)
    assert r.valido, r.para_dict()

@pytest.mark.parametrize("arq", INVALIDOS, ids=lambda p: p.name)
def test_exemplo_invalido_falha_exatamente_na_regra_esperada(arq):
    d = carregar(arq); doc, esp = d["documento"], d["_esperado"]
    r = validar_modelo(doc) if "objetos" in doc else validar(doc)
    assert not r.valido
    assert {(e.codigo, e.regra) for e in r.erros} == {(esp["codigo"], esp["regra"])}

def test_cada_invariante_tem_exemplo_invalido():
    cobertas = {carregar(a)["_esperado"]["regra"] for a in INVALIDOS}
    assert cobertas >= {f"INV-{n:02d}" for n in range(2, 16)}
