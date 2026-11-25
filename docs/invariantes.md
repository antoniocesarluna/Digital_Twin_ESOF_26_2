# Invariantes do Campus Domain

| ID | Invariante | Verificada em | Código de erro | Origem |
|---|---|---|---|---|
| INV-01 | Todo objeto tem identificador IRI único e estável. | Schema + serviço | G1-SCH-001 / G1-ESP-001 | RN-01 |
| INV-02 | Toda geometria está na área de interesse do campus. | Serviço | G1-ESP-002 | RN-02 |
| INV-03 | Polígonos fechados, válidos, com área maior que zero. | Biblioteca | G1-GEO-003 | RN-03 |
| INV-04 | Pavimento contido na projeção da sua edificação. | Agregado | G1-AGR-004 | RN-04 |
| INV-05 | Número do pavimento único na edificação. | Agregado | G1-AGR-005 | RN-05 |
| INV-06 | Via não atravessa edificação. | Serviço | G1-ESP-006 | RN-06 |
| INV-07 | Ponto de interesse tem categoria; portaria tem número e endereço. | Schema + agregado | G1-SCH-001 | RN-07 |
| INV-08 | Área verde não se sobrepõe a edificação. | Serviço | G1-ESP-008 | RN-08 |
| INV-09 | Categorias pertencem ao vocabulário controlado. | Schema (enum) | G1-SCH-001 | RN-09 |
| INV-10 | CRS é EPSG:31983. | Schema (const) | G1-SCH-001 | RN-10 |
| INV-11 | Número do mapa único entre internas; externas únicas por endereço. | Serviço | G1-ESP-011 | Mapa (A1) |
| INV-12 | Interna dentro do perímetro; externa fora dele. | Serviço | G1-ESP-012 | Mapa |
| INV-13 | Portaria a no máximo 5 m do perímetro. | Serviço | G1-ESP-013 | Mapa (A3) |
| INV-14 | Edificação externa tem endereço. | Schema + agregado | G1-SCH-001 | Mapa |
| INV-15 | Externa: número do mapa igual ao número do endereço. | Agregado | G1-AGR-015 | Mapa (A2) |
| INV-16 | Histórico: versões 1..n sem lacunas, períodos contíguos, só a vigente em aberto. | Biblioteca | G1-HIS-016 | RF14 (prof.) |
| INV-17 | Eventos coerentes: versão avança 1; PavimentoAdicionado só em edificação. | Biblioteca | G1-EVT-017 | RF05 (prof.) |
