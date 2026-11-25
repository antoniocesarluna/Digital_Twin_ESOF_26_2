# Linguagem ubíqua — Campus Domain

Contrato v1.0.0 · Revisão 2 (25 de novembro de 2026)

| Termo | Termo no código | Definição | CityGML 3.0 | Exemplo do campus |
|---|---|---|---|---|
| Campus | `Campus` | Área delimitada por perímetro onde estão as edificações internas; referência espacial do modelo. | core:CityModel | Campus Higienópolis |
| Perímetro do Campus | `perimetro` | Polígono limitado pelas ruas Itambé, Maria Antônia, da Consolação e Piauí; separa edificações internas e externas. | gml:Polygon | — |
| Área de Interesse | `areaDeInteresse` | Retângulo envolvente que contém o perímetro e todas as edificações externas mapeadas; nenhuma geometria pode ficar fora dele. | gml:Envelope [E] | da R. Piauí (oeste) à R. Maria Borba (leste) |
| Edificação | `Edificacao` | Construção identificada no mapa por número, com uso principal definido. | bldg:Building | 31 — FCI |
| Edificação Interna | `localizacao = interna` | Edificação dentro do perímetro, numerada na sequência do mapa. | gen:genericAttribute [G] | 41 — Ed. João Calvino |
| Edificação Externa | `localizacao = externa` | Edificação fora do perímetro; o número do mapa é o número do endereço. | gen:genericAttribute [G] | 40 — R. Maria Borba, 40 |
| Número do Mapa | `numeroMapa` | Rótulo usado no mapa e na sinalização. Não é identificador global. | gen:genericAttribute [G] | 40 interna e 40 externa |
| Homenageado | `homenageado` | Nome próprio do edifício ("Ed. ..."). | gen:genericAttribute [G] | Ed. Paulo Breda Filho |
| Unidade Ocupante | `unidadesOcupantes` | Unidade acadêmica ou administrativa que usa a edificação ou o pavimento. | gen:genericAttribute [G] | CGPOS no 8º pav. do 41 |
| Pavimento | `Pavimento` | Andar de uma edificação; térreo = 0, subsolos negativos. | bldg:Storey | 8º pavimento do 41 |
| Via | `Via` | Logradouro público ou circulação interna, representada por seu eixo. | tran:Road | Rua da Consolação |
| Revestimento | `revestimento` | Material da superfície da via. | gen:genericAttribute [G] | asfalto |
| Ponto de Interesse | `PontoDeInteresse` | Local pontual relevante ao usuário, com categoria controlada. | gen:GenericOccupiedSpace | Achados e Perdidos (35) |
| Portaria | `categoria = portaria` | Acesso controlado no perímetro, com número de portaria (01–07) e endereço. | idem | Portaria 07 — R. da Consolação 930 |
| Área Verde | `AreaVerde` | Superfície com cobertura vegetal predominante. | veg:PlantCover | bosque do setor norte |
| Categoria de Uso | `categoriaUso` | Uso principal da edificação (vocabulário controlado). | bldg:function | ensino, educacao-basica |
| Rótulo | `rotulo` | Nome de exibição de um termo de vocabulário, usado obrigatoriamente pelo G5 em filtros, legendas e popups. | — | educacao-basica → Educação básica (Colégio) |
| Situação | `situacao` | Estado no ciclo de vida: ativo, planejado, em-obra, desativado. | creationDate / terminationDate | ativo |
| Versão do Objeto | `metadados.versao` | Retrato completo de um objeto num período de validade; cada alteração cria uma nova versão. | core:validFrom / validTo | 41: v1 (2024) e v2 (2026) |
| Evento de Domínio | `evento-de-dominio` | Fato relevante ocorrido com um objeto urbano, publicado pelo G3 para os demais grupos. | — (fora do CityGML) | PavimentoAdicionado no 41 |
| Identificador | `id` | IRI estável e único do objeto urbano. | gml:identifier | urn:upm:campus-hig:edificacao:31 |

## Legenda

- **ADE** — Application Domain Extension. Mecanismo oficial do CityGML para estender o padrão com classes e atributos de um domínio específico, publicados num XSD adicional (há ADEs de energia, ruído e redes de utilidades, por exemplo). A v0.1.0 previa uma ADE do campus; com a decisão de manter apenas JSON Schema como contrato (ADR-009), ela não será criada.
- **[G]** — gen:genericAttribute. Atributo genérico do módulo Generics do CityGML (nome, tipo e valor), que registra um dado sem classe própria no padrão sem exigir extensão. É assim que os atributos do campus aparecem no CityGML exportado.
- **[E]** — gml:Envelope. Retângulo alinhado aos eixos do sistema de coordenadas, definido por dois cantos (inferior esquerdo e superior direito): a "caixa envolvente" ou bounding box. Delimita uma extensão espacial; não representa uma construção.

## Termos proibidos

prédio, bloco (use Edificação); andar (Pavimento); pavimentação (Revestimento); portão, entrada (Portaria); POI em textos em português (Ponto de Interesse); código do prédio (Número do Mapa ou Identificador).
