# Campus Domain — Grupo 1 · Gêmeo Digital Urbano do Campus

Bounded Context **Campus Domain** (Core Domain & Ontologia GML) do projeto da disciplina de Engenharia de Software
do PPGCA/Mackenzie. Integrantes: Antonio César Luna e Rodolfo Marino de Oliveira.

**Contrato v1.0.0 — aprovado pelos professores e pelos grupos consumidores.** JSON Schema é o único contrato (ADR-009).

## Conteúdo

| Pasta | O que tem | Consumidores |
|---|---|---|
| `schemas/json/` | JSON Schema 2020-12: objetos, modelo do campus, histórico, eventos, vocabulário, relatório | todos |
| `schemas/vocab/` | Vocabulários controlados com rótulos (consumo **obrigatório** pelo G5) e `index.json` | G4, G5 |
| `schemas/jsonld/` | `@context` JSON-LD (termos da linguagem ubíqua → IRIs) | G4 |
| `examples/` | Exemplos válidos e inválidos (um por invariante) derivados do mapa do campus | G2, G3 |
| `campus_domain/` | Biblioteca: domínio, validação, GeoJSON, CityGML, histórico, eventos, auditoria, serviço HTTP | G3 |
| `openapi/` | OpenAPI 3.1 do serviço, com exemplos reais (base do mock Prism) | G3, G5 |
| `docs/` | Linguagem ubíqua, invariantes, ADRs, respostas dos professores, requisitos complementares | todos |
| `tools/` | Geradores do contrato e do OpenAPI, detector de mudanças incompatíveis, conformidade OGC | CI |

## Uso rápido

    pip install -r requirements.txt
    pytest -q --cov=campus_domain                 # harness completo
    python -m campus_domain.servico --porta 8001  # serviço real
    docker compose -f docker-compose.g1.yml up    # serviço (8001) + mock Prism (4011)

Biblioteca (G3):

    from campus_domain import validar_documento, de_geojson
    docs = de_geojson(feature_desenhada_no_leaflet)          # WGS 84 -> EPSG:31983
    rel = validar_documento(docs[0])
    if not rel.valido: return 422, rel.para_dict()

Serviço (G5): `GET /vocabularios/categoriaUso`, `GET /fixtures/campus?formato=geojson`, `POST /validacao`.

## Versionamento

Política MAJOR/MINOR/PATCH da seção 6.1 do documento do grupo, aplicada no CI por
`tools/detectar_breaking_change.py --base <última tag>`. Tags: `g1-v0.1.0` (apresentada), `g1-v1.0.0` (aprovada).

Geometrias dos exemplos são esquemáticas (mapa ilustrativo, sem base georreferenciada) e definitivas para o projeto (ADR-008).
