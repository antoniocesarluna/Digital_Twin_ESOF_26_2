"""Campus Domain — biblioteca do Grupo 1 (Core Domain & Ontologia GML).
Interface pública estável (RI-07); ver __all__."""
__version__ = "1.0.0"
from .eventos import chave_de_roteamento, criar_evento
from .gerador import gerar_campus
from .mapeamento import de_dict, para_dict
from .serializacao.geojson import de_geojson, para_geojson
from .serializacao.gml import para_gml
from .serializacao.jsonld import para_jsonld
from .validacao import RelatorioDeValidacao, validar, validar_documento, validar_evento, validar_historico, validar_modelo

__all__ = ["validar", "validar_modelo", "validar_historico", "validar_evento", "validar_documento",
           "criar_evento", "chave_de_roteamento", "RelatorioDeValidacao", "de_dict", "para_dict",
           "para_gml", "para_jsonld", "para_geojson", "de_geojson", "gerar_campus"]
