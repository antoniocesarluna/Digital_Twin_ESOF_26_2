"""Testes de contrato do serviço HTTP contra o OpenAPI publicado (RNF10)."""
import json
import threading
import urllib.error
import urllib.request

import pytest
from conftest import RAIZ, carregar
from openapi_spec_validator import validate

from campus_domain.servico import criar_servidor

SPEC = RAIZ / "openapi/campus-domain.openapi.json"

@pytest.fixture(scope="module")
def base():
    srv = criar_servidor(0, "127.0.0.1"); t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"; srv.shutdown()

def chamar(base, rota, corpo=None):
    req = urllib.request.Request(base + rota, data=None if corpo is None else json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json"}, method="GET" if corpo is None else "POST")
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e: return e.code, e.headers, e.read()

def test_openapi_valido():
    validate(json.loads(SPEC.read_text("utf-8")), base_uri=SPEC.as_uri())

def test_rotas_documentadas_respondem_com_status_documentado(base):
    api = json.loads(SPEC.read_text("utf-8")); ed31 = carregar("examples/valid/edificacao-31.json")
    for caminho, ops in api["paths"].items():
        rota = caminho.replace("{nome}", "categoriaUso" if "vocab" in caminho else "edificacao")
        for metodo, op in ops.items():
            corpo = None if metodo == "get" else (ed31 if "contrato" not in rota else op["requestBody"]["content"]["application/json"]["example"])
            status, _, _ = chamar(base, rota, corpo)
            assert str(status) in op["responses"], f"{metodo.upper()} {rota} -> {status}"

def test_g5_recebe_vocabulario_com_cors(base):
    status, h, corpo = chamar(base, "/vocabularios/categoriaUso")
    assert status == 200 and h["Access-Control-Allow-Origin"] == "*"
    assert {t["codigo"] for t in json.loads(corpo)["termos"]} >= {"ensino", "educacao-basica"}

def test_validacao_rejeitada_devolve_422_com_relatorio(base):
    status, _, corpo = chamar(base, "/validacao", carregar("examples/invalid/inv-04-pavimento-fora-da-edificacao.json")["documento"])
    assert status == 422 and json.loads(corpo)["erros"][0]["regra"] == "INV-04"

def test_fixtures_sinteticas_em_geojson(base):
    status, h, corpo = chamar(base, "/fixtures/campus?sinteticos=10&semente=7&formato=geojson")
    assert status == 200 and len(json.loads(corpo)["features"]) == len(carregar("examples/valid/modelo-campus-higienopolis.json")["objetos"]) + 10

def test_exportacao_citygml(base):
    status, h, corpo = chamar(base, "/exportacao/citygml", carregar("examples/valid/modelo-campus-higienopolis.json"))
    assert status == 200 and h["Content-Type"].startswith("application/gml+xml") and b"tran:Road" in corpo

def test_json_invalido_400_e_rota_inexistente_404(base):
    req = urllib.request.Request(base + "/validacao", data=b"{x", method="POST")
    with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
    assert e.value.code == 400 and chamar(base, "/nada")[0] == 404

def test_nao_serve_arquivos_fora_do_contrato(base):
    assert chamar(base, "/schemas/..%2F..%2Fcampus_domain%2Fservico")[0] == 404
