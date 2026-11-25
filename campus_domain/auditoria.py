"""RNF11 — logs estruturados (uma linha JSON por evento) no logger 'campus_domain.auditoria'.
Registra validações (aceitas e rejeitadas, com código e invariante de cada falha) e
transformações de formato. Quem integra (G3, serviço HTTP) escolhe o destino do log."""
import functools
import json
import logging
import threading
import time
from datetime import datetime, timezone

LOGGER = logging.getLogger("campus_domain.auditoria")
LOGGER.addHandler(logging.NullHandler())   # biblioteca não imprime nada até o integrador configurar o log
_local = threading.local()

def registrar(evento: str, nivel: int = logging.INFO, **campos):
    if LOGGER.isEnabledFor(nivel):
        LOGGER.log(nivel, json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                                      "evento": evento, **campos}, ensure_ascii=False))

def _tipo(doc):
    if not isinstance(doc, dict): return "desconhecido"
    if "objetos" in doc: return "modelo"
    if "versoes" in doc: return "historico"
    if "idEvento" in doc: return "evento"
    return doc.get("tipo", "desconhecido")

def auditar_validacao(func):
    """Registra apenas a chamada mais externa (validar_historico chama validar internamente)."""
    @functools.wraps(func)
    def inner(doc, *a, **k):
        if getattr(_local, "ativo", False): return func(doc, *a, **k)
        _local.ativo = True; t0 = time.perf_counter()
        try:
            rel = func(doc, *a, **k)
        finally:
            _local.ativo = False
        oid = doc.get("id") or doc.get("objetoId") if isinstance(doc, dict) else None
        registrar("validacao", logging.INFO if rel.valido else logging.WARNING, funcao=func.__name__,
                  tipoDocumento=_tipo(doc), objetoId=oid, resultado="aceito" if rel.valido else "rejeitado",
                  erros=[{"codigo": e.codigo, "regra": e.regra, "local": e.local} for e in rel.erros],
                  duracaoMs=round((time.perf_counter() - t0) * 1000, 2))
        return rel
    return inner

def auditar_transformacao(origem: str, destino: str):
    def deco(func):
        @functools.wraps(func)
        def inner(*a, **k):
            r = func(*a, **k)
            n = len(r["features"]) if isinstance(r, dict) and "features" in r else (len(r) if isinstance(r, list) else 1)
            registrar("transformacao", origem=origem, destino=destino, funcao=func.__name__, quantidade=n)
            return r
        return inner
    return deco
