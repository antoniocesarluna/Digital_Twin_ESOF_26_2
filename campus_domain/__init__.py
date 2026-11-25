"""Campus Domain — biblioteca do Grupo 1 (Core Domain & Ontologia GML).
Interface pública estável (RI-07): validar, validar_modelo, para_gml, para_jsonld,
de_dict, para_dict, gerar_campus."""
from .validacao import validar, validar_modelo, RelatorioDeValidacao
from .mapeamento import de_dict, para_dict
from .serializacao.gml import para_gml
from .serializacao.jsonld import para_jsonld
from .gerador import gerar_campus
__version__ = "0.1.0"
__all__ = ["validar", "validar_modelo", "RelatorioDeValidacao", "de_dict", "para_dict",
           "para_gml", "para_jsonld", "gerar_campus"]
