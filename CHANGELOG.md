# Changelog — Contrato Campus Domain (Grupo 1)

## [1.0.0] — 2026-11-25 — contrato aprovado
Ajustes pedidos na apresentação de 24/11/2026 e requisitos complementares do professor.
### Removido (incompatível)
- `schemas/xsd/campus-ade.xsd`: JSON Schema passa a ser o único contrato (ADR-009).
- `Metadados` deixa de aceitar campos não previstos.
### Adicionado
- Vocabulários com rótulos, `vocabulario.schema.json` e `index.json`; consumo obrigatório pelo G5 (ADR-010).
- `historico-do-objeto.schema.json` e INV-16 (RF14); `Metadados.alteradoPor` e `DataHora`.
- `evento-de-dominio.schema.json` e INV-17 (nota RF05); `criar_evento()` com chave `campus.<tipo>`.
- `relatorio-de-validacao.schema.json`.
- Exportação GeoJSON (WGS 84) e importação para o contrato (RF10, RF12); CityGML para os quatro tipos.
- Logs estruturados de validações e transformações (RNF11).
- Serviço HTTP, OpenAPI 3.1, mock Prism, Dockerfile e `docker-compose.g1.yml` (RNF07, RNF10).
- `tools/detectar_breaking_change.py`, `tools/validar_gml_ogc.py`, `pyproject.toml`.

## [0.1.0] — 2026-11-24 — versão apresentada
- JSON Schema 2020-12, XSD do perfil (ADE), @context JSON-LD, vocabulários.
- 13 exemplos válidos e 15 inválidos derivados do mapa do Campus Higienópolis.
- Biblioteca campus_domain e pipeline de CI.
