"""Harness do contrato: schemas válidos, vocabulários sincronizados, exemplos coerentes."""
import json

import pytest
from conftest import RAIZ, carregar
from jsonschema import Draft202012Validator

from campus_domain import validar_documento

SCHEMAS = sorted((RAIZ / "schemas/json").glob("*.schema.json"))
VALIDOS = sorted((RAIZ / "examples/valid").glob("*.json"))
INVALIDOS = sorted((RAIZ / "examples/invalid").glob("*.json"))

@pytest.mark.parametrize("arq", SCHEMAS, ids=lambda p: p.name)
def test_schema_conforme_metaschema_2020_12(arq):
    Draft202012Validator.check_schema(json.loads(arq.read_text("utf-8")))

def test_contrato_tem_apenas_json_schema():
    """ADR-009: decisão dos professores (25/11/2026) — JSON Schema é o único contrato."""
    assert not (RAIZ / "schemas/xsd").exists()

@pytest.mark.parametrize("vocab,campo,arq", [
    ("categoriaUso", "categoriaUso", "edificacao"), ("categoriaPontoDeInteresse", "categoria", "ponto-de-interesse"),
    ("classeVia", "classe", "via"), ("coberturaVegetal", "cobertura", "area-verde")])
def test_vocabulario_sincronizado_com_schema(vocab, campo, arq):
    termos = [t["codigo"] for t in carregar(f"schemas/vocab/{vocab}.json")["termos"]]
    assert carregar(f"schemas/json/{arq}.schema.json")["properties"][campo]["enum"] == termos

@pytest.mark.parametrize("arq", sorted((RAIZ / "schemas/vocab").glob("[!i]*.json")), ids=lambda p: p.name)
def test_vocabulario_conforme_schema_e_com_rotulos_unicos(arq):
    """G5 consome obrigatoriamente os vocabulários (ADR-010): rótulos completos e sem duplicidade."""
    v = carregar(arq)
    Draft202012Validator(carregar("schemas/json/vocabulario.schema.json")).validate(v)
    rotulos = [t["rotulo"] for t in v["termos"]]
    assert len(rotulos) == len(set(rotulos))

def test_indice_de_vocabularios_completo():
    idx = carregar("schemas/vocab/index.json")
    assert {v["arquivo"] for v in idx["vocabularios"]} == {p.name for p in (RAIZ / "schemas/vocab").glob("[!i]*.json")}

def test_contexto_jsonld_cobre_termos_dos_schemas():
    ctx = carregar("schemas/jsonld/context.jsonld")["@context"]
    for arq in ("edificacao", "via", "ponto-de-interesse", "area-verde"):
        props = carregar(f"schemas/json/{arq}.schema.json")["properties"]
        faltando = [p for p in props if p not in ctx]
        assert not faltando, f"{arq}: termos sem IRI no @context: {faltando}"

@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_exemplo_valido_passa(arq):
    r = validar_documento(carregar(arq))
    assert r.valido, r.para_dict()

@pytest.mark.parametrize("arq", INVALIDOS, ids=lambda p: p.name)
def test_exemplo_invalido_falha_exatamente_na_regra_esperada(arq):
    d = carregar(arq); doc, esp = d["documento"], d["_esperado"]
    r = validar_documento(doc)
    assert not r.valido
    assert {(e.codigo, e.regra) for e in r.erros} == {(esp["codigo"], esp["regra"])}

def test_relatorios_seguem_o_schema_publicado():
    v = Draft202012Validator(carregar("schemas/json/relatorio-de-validacao.schema.json"))
    for arq in INVALIDOS:
        v.validate(validar_documento(carregar(arq)["documento"]).para_dict())

def test_cada_invariante_tem_exemplo_invalido():
    cobertas = {carregar(a)["_esperado"]["regra"] for a in INVALIDOS}
    assert cobertas >= {f"INV-{n:02d}" for n in range(2, 18)}
