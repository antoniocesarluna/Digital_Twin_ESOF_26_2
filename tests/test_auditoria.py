"""RNF11: logs estruturados de validações e transformações."""
import json
import logging

from conftest import carregar

from campus_domain import para_geojson, validar, validar_historico


def _linhas(caplog): return [json.loads(r.getMessage()) for r in caplog.records if r.name == "campus_domain.auditoria"]

def test_rejeicao_geometrica_registrada_como_warning(caplog):
    caplog.set_level(logging.INFO, logger="campus_domain.auditoria")
    doc = carregar("examples/invalid/inv-03-poligono-autointersecao.json")["documento"]
    validar(doc)
    [linha] = _linhas(caplog)
    assert linha["resultado"] == "rejeitado" and linha["erros"][0]["regra"] == "INV-03"
    assert caplog.records[-1].levelno == logging.WARNING and linha["objetoId"].endswith(":31")

def test_validacao_aninhada_registra_uma_unica_linha(caplog):
    caplog.set_level(logging.INFO, logger="campus_domain.auditoria")
    validar_historico(carregar("examples/valid/historico-edificacao-41.json"))
    assert [l["funcao"] for l in _linhas(caplog)] == ["validar_historico"]

def test_transformacao_registrada(caplog, modelo):
    caplog.set_level(logging.INFO, logger="campus_domain.auditoria")
    para_geojson(modelo)
    [linha] = _linhas(caplog)
    assert linha["evento"] == "transformacao" and linha["quantidade"] == len(modelo["objetos"])
