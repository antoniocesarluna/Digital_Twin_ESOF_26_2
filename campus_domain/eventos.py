"""Criação de eventos de domínio conforme evento-de-dominio.schema.json.
O G3 publica no broker (RabbitMQ ou Redis Pub/Sub) com a chave de roteamento campus.<tipo>."""
import uuid
from datetime import datetime, timezone

from . import __version__
from .validacao import validar_evento


def chave_de_roteamento(evento: dict) -> str:
    return "campus." + evento["tipo"]

def criar_evento(tipo: str, objeto_id: str, dados: dict, grupo: str = "G3", usuario: str | None = None) -> dict:
    origem = {"grupo": grupo} | ({"usuario": usuario} if usuario else {})
    evt = {"idEvento": str(uuid.uuid4()), "tipo": tipo, "versaoContrato": __version__,
           "ocorridoEm": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "origem": origem, "objetoId": objeto_id, "dados": dados}
    rel = validar_evento(evt)
    if not rel.valido:
        raise ValueError(rel.para_dict())
    return evt
