import pytest
from conftest import carregar

from campus_domain import chave_de_roteamento, criar_evento, validar_evento, validar_historico


@pytest.fixture
def hist(): return carregar("examples/valid/historico-edificacao-41.json")

def test_historico_valido_tem_versao_vigente_aberta(hist):
    assert validar_historico(hist).valido and "validoAte" not in hist["versoes"][-1]

def test_inv16_periodos_nao_contiguos(hist):
    hist["versoes"][0]["validoAte"] = "2026-11-24T10:00:00-03:00"
    assert {e.regra for e in validar_historico(hist).erros} == {"INV-16"}

def test_inv16_versao_vigente_com_fim(hist):
    hist["versoes"][1]["validoAte"] = "2027-01-01T00:00:00-03:00"
    assert not validar_historico(hist).valido

def test_inv16_versao_de_outro_objeto(hist):
    hist["versoes"][1]["objeto"]["id"] = "urn:upm:campus-hig:edificacao:31"
    assert any(e.local.endswith("/objeto/id") for e in validar_historico(hist).erros)

def test_historico_propaga_regras_do_agregado(hist):
    hist["versoes"][1]["objeto"]["pavimentos"][0]["numero"] = 8
    assert {e.regra for e in validar_historico(hist).erros} == {"INV-05"}

def test_criar_evento_valido_e_roteamento():
    e = criar_evento("PavimentoAdicionado", "urn:upm:campus-hig:edificacao:41",
                     {"pavimentoId": "urn:upm:campus-hig:pavimento:41-9", "numero": 9}, usuario="gestor.suinf")
    assert validar_evento(e).valido and chave_de_roteamento(e) == "campus.PavimentoAdicionado"

def test_inv17_pavimento_em_objeto_que_nao_e_edificacao():
    with pytest.raises(ValueError, match="INV-17"):
        criar_evento("PavimentoAdicionado", "urn:upm:campus-hig:via:rua-itambe",
                     {"pavimentoId": "urn:upm:campus-hig:pavimento:x-1", "numero": 1})

def test_evento_com_dados_de_outro_tipo_falha_no_schema():
    with pytest.raises(ValueError):
        criar_evento("ObjetoUrbanoDesativado", "urn:upm:campus-hig:edificacao:31", {"versao": 1})
