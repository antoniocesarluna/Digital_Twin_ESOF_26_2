"""Gera openapi/campus-domain.openapi.json (OpenAPI 3.1) a partir do contrato e das fixtures.
Os exemplos embutidos permitem subir um mock com Prism sem o serviço real (RNF10)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(RAIZ))
from campus_domain import __version__, para_geojson, validar_documento

ld = lambda r: json.loads((RAIZ / r).read_text("utf-8"))
SJ = "../schemas/json/"
modelo = ld("examples/valid/modelo-campus-higienopolis.json")
ed31 = ld("examples/valid/edificacao-31.json")
inv04 = ld("examples/invalid/inv-04-pavimento-fora-da-edificacao.json")["documento"]
feat = para_geojson(ed31)
J = lambda schema, ex=None, tipo="application/json": {tipo: {"schema": schema, **({"example": ex} if ex is not None else {})}}
ERRO = {"description": "Requisição inválida", "content": J({"type": "object", "properties": {"erro": {"type": "string"}}}, {"erro": "JSON inválido"})}
DOC = {"oneOf": [{"$ref": SJ + f} for f in ("edificacao.schema.json", "via.schema.json", "ponto-de-interesse.schema.json",
       "area-verde.schema.json", "modelo-do-campus.schema.json", "historico-do-objeto.schema.json", "evento-de-dominio.schema.json")]}
REL = {"$ref": SJ + "relatorio-de-validacao.schema.json"}
GEO = {"type": "object", "required": ["type"], "properties": {"type": {"enum": ["FeatureCollection", "Feature"]}}}
api = {"openapi": "3.1.0", "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
 "info": {"title": "Campus Domain — Grupo 1", "version": __version__,
          "description": "Published Language do Bounded Context Campus Domain: vocabulários (consumo obrigatório pelo G5), "
                         "schemas, fixtures, validação e conversões. Mock: prism mock openapi/campus-domain.openapi.json"},
 "servers": [{"url": "http://localhost:8001", "description": "serviço real (python -m campus_domain.servico)"},
             {"url": "http://localhost:4011", "description": "mock Prism (docker-compose.g1.yml)"}],
 "tags": [{"name": "Vocabulários", "description": "G5 — filtros, legendas e popups"}, {"name": "Contrato"},
          {"name": "Validação", "description": "G3 — antes de persistir no G2"}, {"name": "Conversão e exportação"}, {"name": "Fixtures"}],
 "paths": {
  "/saude": {"get": {"operationId": "saude", "tags": ["Contrato"], "summary": "Estado do serviço e versão do contrato",
     "responses": {"200": {"description": "OK", "content": J({"type": "object"}, {"status": "ok", "versaoContrato": __version__})}}}},
  "/vocabularios": {"get": {"operationId": "listarVocabularios", "tags": ["Vocabulários"], "summary": "Índice dos vocabulários controlados",
     "responses": {"200": {"description": "Índice", "content": J({"type": "object"}, ld("schemas/vocab/index.json"))}}}},
  "/vocabularios/{nome}": {"get": {"operationId": "obterVocabulario", "tags": ["Vocabulários"], "summary": "Termos com código, rótulo e definição",
     "parameters": [{"name": "nome", "in": "path", "required": True, "schema": {"enum": [v["nome"] for v in ld("schemas/vocab/index.json")["vocabularios"]]}}],
     "responses": {"200": {"description": "Vocabulário", "content": J({"$ref": SJ + "vocabulario.schema.json"}, ld("schemas/vocab/categoriaUso.json"))},
                   "404": {"description": "Vocabulário inexistente"}}}},
  "/schemas/{nome}": {"get": {"operationId": "obterSchema", "tags": ["Contrato"], "summary": "JSON Schema do contrato",
     "parameters": [{"name": "nome", "in": "path", "required": True, "schema": {"type": "string"}, "example": "edificacao"}],
     "responses": {"200": {"description": "JSON Schema 2020-12", "content": J({"type": "object"})}, "404": {"description": "Schema inexistente"}}}},
  "/fixtures/campus": {"get": {"operationId": "obterFixtures", "tags": ["Fixtures"], "summary": "Modelo do campus para testes de integração",
     "parameters": [{"name": "sinteticos", "in": "query", "schema": {"type": "integer", "minimum": 0, "maximum": 200, "default": 0}},
                    {"name": "semente", "in": "query", "schema": {"type": "integer", "default": 42}},
                    {"name": "formato", "in": "query", "schema": {"enum": ["contrato", "geojson"], "default": "contrato"}}],
     "responses": {"200": {"description": "Modelo do campus", "content": {**J({"$ref": SJ + "modelo-do-campus.schema.json"}, modelo),
                                                                         **J(GEO, para_geojson(modelo), "application/geo+json")}}}}},
  "/validacao": {"post": {"operationId": "validar", "tags": ["Validação"], "summary": "Valida objeto, modelo, histórico ou evento",
     "requestBody": {"required": True, "content": J(DOC, ed31)},
     "responses": {"200": {"description": "Documento aceito", "content": J(REL, {"valido": True, "erros": []})},
                   "422": {"description": "Documento rejeitado", "content": J(REL, validar_documento(inv04).para_dict())},
                   "400": ERRO}}},
  "/conversao/geojson": {"post": {"operationId": "paraGeoJSON", "tags": ["Conversão e exportação"], "summary": "Contrato (EPSG:31983) → GeoJSON (WGS 84)",
     "requestBody": {"required": True, "content": J(DOC, ed31)},
     "responses": {"200": {"description": "FeatureCollection", "content": J(GEO, feat, "application/geo+json")}, "400": ERRO}}},
  "/conversao/contrato": {"post": {"operationId": "deGeoJSON", "tags": ["Conversão e exportação"], "summary": "GeoJSON desenhado no Leaflet → documentos do contrato",
     "requestBody": {"required": True, "content": J(GEO, feat, "application/geo+json") | J(GEO, feat)},
     "responses": {"200": {"description": "Documentos em EPSG:31983", "content": J({"type": "object", "properties": {"documentos": {"type": "array"}}}, {"documentos": [ed31]})}, "400": ERRO}}},
  "/exportacao/citygml": {"post": {"operationId": "exportarCityGML", "tags": ["Conversão e exportação"], "summary": "Exporta CityGML 3.0 (QGIS, 3DCityDB)",
     "requestBody": {"required": True, "content": J(DOC, modelo)},
     "responses": {"200": {"description": "core:CityModel", "content": J({"type": "string"}, None, "application/gml+xml")}, "400": ERRO}}}}}
out = RAIZ / "openapi" / "campus-domain.openapi.json"; out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(api, ensure_ascii=False, indent=2) + "\n", "utf-8"); print("openapi", __version__)
