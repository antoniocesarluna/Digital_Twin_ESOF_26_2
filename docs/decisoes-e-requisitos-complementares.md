# Respostas dos professores (24/11/2026)

| Pergunta | Resposta | Impacto |
|---|---|---|
| A "ontologia" esperada é o modelo alinhado ao CityGML com JSON-LD ou uma ontologia formal em OWL? | Alinhado ao CityGML com JSON-LD. | Nível 2 confirmado; OWL/SHACL deixa de ser diferencial planejado. |
| Devem ser mantidos XSD e JSON Schema, ou um deles basta? | Manter apenas JSON Schema. | XSD e ADE removidos (ADR-009); GML continua como formato de exportação. |
| Quem aprova o contrato e as mudanças posteriores? | Professores e grupos consumidores. O contrato já foi aprovado; faltam apenas os ajustes. | Contrato publicado como 1.0.0 (ADR-013); mudanças seguem a política da seção 6.1. |
| Existe base georreferenciada que substitua as geometrias esquemáticas? | Não; manter a atual. | ADR-008 passa de temporária a definitiva para o projeto. |
| A integração entre as equipes 1, 2 e 5 indica que o G5 consome os vocabulários do G1? | Sim, obrigatoriamente. | Vocabulários com rótulos, schema e rota GET /vocabularios (ADR-010). |

# Requisitos complementares enviados pelo professor

| Requisito | Tema | Aplica-se ao G1 | Atendimento | Evidência |
|---|---|---|---|---|
| RF10 | Interface gráfica Leaflet ↔ Ingestão | Parcial | G5 desenha e G3 ingere. O G1 converte o GeoJSON desenhado (WGS 84) para o contrato, fornece os vocabulários do formulário e devolve o relatório de erros em português. | de_geojson(); POST /conversao/contrato; teste test_desenho_do_leaflet_vira_objeto_valido |
| RF11 | Busca espacial por bounding box e raio | Indireta | Implementada pelo G4. O G1 garante CRS métrico (raio em metros) e geometrias válidas; a Área de Interesse delimita o domínio da busca. | ADR-003; INV-02, INV-03 |
| RF12 | Exportação em padrões abertos | Sim | CityGML 3.0 para os quatro tipos de objeto e GeoJSON RFC 7946 (QGIS, Leaflet). | para_gml(); para_geojson(); POST /exportacao/citygml; GET /fixtures/campus?formato=geojson |
| RF13 | Controle de acesso e perfis | Não | Perfis pertencem ao contexto de identidade (G3/G5), não ao Campus Domain. O G1 registra quem alterou cada versão (alteradoPor) para auditoria. | Metadados.alteradoPor; historico-do-objeto.schema.json |
| RF14 | Versionamento e histórico | Sim | Schema de histórico, INV-16, validar_historico() e evento GeometriaAtualizada; alinhado a validFrom/validTo do CityGML 3.0. | ADR-011; examples/valid/historico-edificacao-41.json |
| RNF09 | Conformidade OGC | Sim | CityGML 3.0 sobre GML 3.2. SIRGAS 2000 é o datum; a projeção canônica é UTM 23S (EPSG:31983). WGS 84 (EPSG:4326) só no GeoJSON/Leaflet. | ADR-001, ADR-003; tools/validar_gml_ogc.py |
| RNF10 | Mocks e fixtures | Sim | OpenAPI 3.1 com exemplos reais, mock Prism e fixtures reais ou sintéticas por rota. | openapi/campus-domain.openapi.json; docker-compose.g1.yml; GET /fixtures/campus |
| RNF11 | Auditoria e logs | Sim (parte do G1) | Uma linha JSON por validação (aceita ou rejeitada, com código e invariante) e por transformação de formato. Escritas no banco são registradas pelo G2/G3. | campus_domain/auditoria.py; tests/test_auditoria.py |
| Nota RF03 | Extensões de arquivos vetoriais | Parcial | O G1 lê .geojson e exporta .gml; .kml e .dxf são convertidos pelo G3 para GeoJSON antes de chamar o G1. | de_geojson(); para_gml() |
| Nota RF05 | Eventos de domínio (faz sentido?) | Sim | Sim. O G1 define o schema dos eventos; o G3 publica num broker leve com chave campus.<tipo>. | evento-de-dominio.schema.json; criar_evento(); ADR-012 |
| Nota RNF07 | Docker | Parcial | Dockerfile e docker-compose.g1.yml prontos para unir ao compose do 3DCityDB disponibilizado pelo professor. | Dockerfile; docker-compose.g1.yml |
