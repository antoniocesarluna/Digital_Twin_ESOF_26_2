"""Gera o contrato v0.1.0 do Campus Domain (schemas, vocabulários, @context, XSD)
e os exemplos válidos/inválidos derivados do mapa do Campus Higienópolis.
As geometrias são ESQUEMÁTICAS: posições do mapa ilustrativo convertidas para
SIRGAS 2000 / UTM 23S por transformação afim aproximada (sem georreferenciamento)."""
import copy
import json
import pathlib

from pyproj import Transformer

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSAO = "1.0.0"
BASE = "https://gemeo-campus.example/schemas/" + VERSAO + "/"
CRS = "EPSG:31983"

def dump(rel, obj):
    p = ROOT / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------------- vocabulários controlados ----------------
VOCAB = {
 "categoriaUso": {
   "ensino": "Edificação destinada predominantemente a aulas de graduação ou pós-graduação.",
   "pesquisa": "Laboratórios e núcleos de pesquisa e inovação.",
   "administrativo": "Serviços administrativos, atendimento e apoio.",
   "cultural": "Centros culturais, históricos, bibliotecas e auditórios.",
   "religioso": "Capela e espaços de culto.",
   "esportivo": "Ginásios e instalações esportivas cobertas.",
   "alimentacao": "Lanchonetes e restaurantes.",
   "educacao-basica": "Edificações do Colégio Presbiteriano Mackenzie.",
   "misto": "Edificação com mais de um uso relevante."},
 "categoriaPontoDeInteresse": {
   "portaria": "Acesso controlado ao campus, identificado por número e endereço.",
   "atendimento": "Balcão de atendimento ao público.",
   "achados-e-perdidos": "Ponto de guarda de objetos encontrados.",
   "alimentacao": "Ponto de venda de alimentos.",
   "auditorio": "Espaço de eventos dentro de uma edificação.",
   "quadra-esportiva": "Quadra descoberta para prática esportiva.",
   "servico": "Outro serviço pontual de apoio."},
 "classeVia": {
   "publica": "Logradouro público que delimita ou dá acesso ao campus.",
   "interna": "Circulação interna de pedestres ou veículos dentro do perímetro."},
 "revestimento": {
   "asfalto": "Revestimento asfáltico.", "concreto": "Piso de concreto.",
   "intertravado": "Blocos intertravados.", "pedra": "Pedra ou paralelepípedo.",
   "nao-informado": "Revestimento ainda não levantado."},
 "coberturaVegetal": {
   "arborea": "Predomínio de árvores.", "gramado": "Predomínio de gramíneas.",
   "jardim": "Canteiros ornamentais.", "misto": "Combinação de coberturas."},
 "situacao": {
   "ativo": "Em uso regular pela universidade.", "planejado": "Aprovado, ainda não construído.",
   "em-obra": "Em construção ou reforma que altera geometria.",
   "desativado": "Fora de uso; mantido para histórico."},
}
# Rótulos de exibição: consumo OBRIGATÓRIO pelo G5 em filtros, legendas e popups (ADR-010)
ROTULOS = {
 "categoriaUso": {"ensino": "Ensino", "pesquisa": "Pesquisa e inovação", "administrativo": "Administrativo",
   "cultural": "Cultural", "religioso": "Religioso", "esportivo": "Esportivo", "alimentacao": "Alimentação",
   "educacao-basica": "Educação básica (Colégio)", "misto": "Uso misto"},
 "categoriaPontoDeInteresse": {"portaria": "Portaria", "atendimento": "Atendimento", "achados-e-perdidos": "Achados e Perdidos",
   "alimentacao": "Alimentação", "auditorio": "Auditório", "quadra-esportiva": "Quadra esportiva", "servico": "Serviço"},
 "classeVia": {"publica": "Via pública", "interna": "Via interna"},
 "revestimento": {"asfalto": "Asfalto", "concreto": "Concreto", "intertravado": "Intertravado", "pedra": "Pedra",
   "nao-informado": "Não informado"},
 "coberturaVegetal": {"arborea": "Arbórea", "gramado": "Gramado", "jardim": "Jardim", "misto": "Mista"},
 "situacao": {"ativo": "Ativo", "planejado": "Planejado", "em-obra": "Em obra", "desativado": "Desativado"},
}
USO_VOCAB = {"categoriaUso": ["Edificacao.categoriaUso"], "categoriaPontoDeInteresse": ["PontoDeInteresse.categoria"],
  "classeVia": ["Via.classe"], "revestimento": ["Via.revestimento"], "coberturaVegetal": ["AreaVerde.cobertura"],
  "situacao": ["Edificacao.situacao"]}
assert all(set(VOCAB[k]) == set(ROTULOS[k]) for k in VOCAB), "todo termo precisa de rótulo"
for k, v in VOCAB.items():
    dump(f"schemas/vocab/{k}.json", {"$schema": BASE + "vocabulario.schema.json", "vocabulario": k, "versao": VERSAO,
         "usadoEm": USO_VOCAB[k],
         "termos": [{"codigo": c, "rotulo": ROTULOS[k][c], "definicao": d} for c, d in v.items()]})
dump("schemas/vocab/index.json", {"versao": VERSAO, "vocabularios": [
     {"nome": k, "arquivo": f"{k}.json", "usadoEm": USO_VOCAB[k], "termos": len(VOCAB[k])} for k in VOCAB]})
VOCAB_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + "vocabulario.schema.json",
  "title": "Vocabulário controlado do Campus Domain (consumo obrigatório pelo G5)", "type": "object",
  "required": ["vocabulario", "versao", "usadoEm", "termos"], "properties": {
    "$schema": {"type": "string"}, "vocabulario": {"type": "string"}, "versao": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "usadoEm": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "termos": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["codigo", "rotulo", "definicao"],
      "additionalProperties": False, "properties": {"codigo": {"type": "string", "pattern": "^[a-z0-9-]+$"},
      "rotulo": {"type": "string", "minLength": 2}, "definicao": {"type": "string", "minLength": 10}}}}}}
enum = lambda k: {"enum": list(VOCAB[k])}

# ---------------- JSON Schema 2020-12 ----------------
ring = {"type": "array", "minItems": 4, "items": {"$ref": "#/$defs/Posicao"}}
COMUM = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "$id": BASE + "comum.schema.json",
 "title": "Campus Domain — Value Objects comuns",
 "$defs": {
  "Identificador": {"type": "string", "description": "IRI estável do objeto urbano (RN-01).",
     "pattern": "^urn:upm:campus-hig:(edificacao|pavimento|via|poi|area-verde|campus):[a-z0-9-]+$"},
  "NumeroMapa": {"type": "integer", "minimum": 1, "maximum": 999,
     "description": "Número do objeto no mapa oficial do campus."},
  "Crs": {"const": CRS, "description": "SIRGAS 2000 / UTM 23S (RN-10)."},
  "Posicao": {"type": "array", "prefixItems": [{"type": "number"}, {"type": "number"}],
              "minItems": 2, "maxItems": 3},
  "Ponto": {"type": "object", "required": ["type", "coordinates"], "additionalProperties": False,
     "properties": {"type": {"const": "Point"}, "coordinates": {"$ref": "#/$defs/Posicao"}}},
  "LinhaPoligonal": {"type": "object", "required": ["type", "coordinates"], "additionalProperties": False,
     "properties": {"type": {"const": "LineString"},
        "coordinates": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/Posicao"}}}},
  "Poligono": {"type": "object", "required": ["type", "coordinates"], "additionalProperties": False,
     "properties": {"type": {"const": "Polygon"},
        "coordinates": {"type": "array", "minItems": 1, "items": ring}}},
  "Endereco": {"type": "object", "required": ["logradouro", "numero"], "additionalProperties": False,
     "properties": {"logradouro": {"type": "string", "minLength": 3},
        "numero": {"type": "string", "pattern": "^[0-9]+[A-Za-z]?$"},
        "complemento": {"type": "string"},
        "municipio": {"const": "São Paulo"}, "uf": {"const": "SP"}}},
  "Situacao": enum("situacao"),
  "DataHora": {"type": "string", "description": "Data e hora ISO 8601 com fuso.",
     "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"},
  "Metadados": {"type": "object", "required": ["versao"], "additionalProperties": False, "properties": {
        "versao": {"type": "integer", "minimum": 1, "description": "Versão do objeto (RF14); incrementa a cada alteração."},
        "atualizadoEm": {"$ref": "#/$defs/DataHora"},
        "alteradoPor": {"type": "string", "description": "Usuário com perfil de gestor que fez a alteração (auditoria)."},
        "fonte": {"type": "string"}}},
 }}
def obj(title, tipo, props, req, extra=None):
    s = {"$schema": "https://json-schema.org/draft/2020-12/schema",
         "$id": BASE + f"{tipo_slug[tipo]}.schema.json", "title": title, "type": "object",
         "required": ["tipo", "id", "crs"] + req, "additionalProperties": False,
         "properties": {"tipo": {"const": tipo}, "id": {"$ref": "comum.schema.json#/$defs/Identificador"},
                        "crs": {"$ref": "comum.schema.json#/$defs/Crs"},
                        "metadados": {"$ref": "comum.schema.json#/$defs/Metadados"}, **props}}
    if extra: s.update(extra)
    return s
tipo_slug = {"Edificacao": "edificacao", "Via": "via", "PontoDeInteresse": "ponto-de-interesse",
             "AreaVerde": "area-verde"}
C = "comum.schema.json#/$defs/"
PAV = {"type": "object", "required": ["id", "numero", "nome", "geometria"], "additionalProperties": False,
       "description": "Entidade interna do agregado Edificação (andar).",
       "properties": {"id": {"$ref": C + "Identificador"}, "numero": {"type": "integer", "minimum": -5, "maximum": 60},
          "nome": {"type": "string"}, "geometria": {"$ref": C + "Poligono"},
          "unidadesOcupantes": {"type": "array", "items": {"type": "string"}}}}
EDF = obj("Edificação", "Edificacao", {
    "numeroMapa": {"$ref": C + "NumeroMapa"}, "nome": {"type": "string", "minLength": 2},
    "homenageado": {"type": "string", "description": "Nome do edifício (ex.: Ed. Paulo Breda Filho)."},
    "localizacao": {"enum": ["interna", "externa"]}, "categoriaUso": enum("categoriaUso"),
    "unidadesOcupantes": {"type": "array", "items": {"type": "string"}},
    "endereco": {"$ref": C + "Endereco"}, "situacao": {"$ref": C + "Situacao"},
    "geometria": {"$ref": C + "Poligono"},
    "pavimentos": {"type": "array", "items": {"$ref": "#/$defs/Pavimento"}}},
    ["numeroMapa", "nome", "localizacao", "categoriaUso", "situacao", "geometria"],
    {"$defs": {"Pavimento": PAV},
     "if": {"properties": {"localizacao": {"const": "externa"}}},
     "then": {"required": ["endereco"]}})
VIA = obj("Via", "Via", {"nome": {"type": "string"}, "classe": enum("classeVia"),
    "revestimento": enum("revestimento"), "geometria": {"$ref": C + "LinhaPoligonal"}},
    ["nome", "classe", "geometria"])
POI = obj("Ponto de Interesse", "PontoDeInteresse", {"nome": {"type": "string"},
    "categoria": enum("categoriaPontoDeInteresse"), "numeroPortaria": {"type": "integer", "minimum": 1},
    "endereco": {"$ref": C + "Endereco"}, "edificacaoRef": {"$ref": C + "Identificador"},
    "geometria": {"$ref": C + "Ponto"}}, ["nome", "categoria", "geometria"],
    {"if": {"required": ["categoria"], "properties": {"categoria": {"const": "portaria"}}},
     "then": {"required": ["numeroPortaria", "endereco"]}})
AV = obj("Área Verde", "AreaVerde", {"nome": {"type": "string"}, "cobertura": enum("coberturaVegetal"),
    "geometria": {"$ref": C + "Poligono"}}, ["nome", "cobertura", "geometria"])
MOD = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + "modelo-do-campus.schema.json",
   "title": "Modelo do Campus (instantâneo para validação de consistência espacial)",
   "type": "object", "required": ["versaoContrato", "campus", "objetos"], "additionalProperties": False,
   "properties": {"versaoContrato": {"const": VERSAO},
     "campus": {"type": "object", "required": ["id", "nome", "crs", "perimetro", "areaDeInteresse"],
        "additionalProperties": False, "properties": {"id": {"$ref": C + "Identificador"},
        "nome": {"type": "string"}, "crs": {"$ref": C + "Crs"}, "perimetro": {"$ref": C + "Poligono"},
        "areaDeInteresse": {"type": "array", "prefixItems": [{"type": "number"}] * 4, "minItems": 4, "maxItems": 4,
            "description": "[minX, minY, maxX, maxY] em EPSG:31983 (RN-02)."}}},
     "objetos": {"type": "array", "items": {"oneOf": [{"$ref": "edificacao.schema.json"}, {"$ref": "via.schema.json"},
         {"$ref": "ponto-de-interesse.schema.json"}, {"$ref": "area-verde.schema.json"}]}}}}
EVENTOS = {
 "ObjetoUrbanoCadastrado": {"required": ["tipoObjeto", "versao"], "properties": {
     "tipoObjeto": {"enum": list(tipo_slug)}, "versao": {"const": 1}}},
 "GeometriaAtualizada": {"required": ["versaoAnterior", "versaoNova"], "properties": {
     "versaoAnterior": {"type": "integer", "minimum": 1}, "versaoNova": {"type": "integer", "minimum": 2}}},
 "PavimentoAdicionado": {"required": ["pavimentoId", "numero"], "properties": {
     "pavimentoId": {"$ref": C + "Identificador"}, "numero": {"type": "integer", "minimum": -5, "maximum": 60}}},
 "ObjetoUrbanoDesativado": {"required": ["motivo"], "properties": {"motivo": {"type": "string", "minLength": 5}}},
}
EVT = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + "evento-de-dominio.schema.json",
  "title": "Evento de domínio do Campus Domain",
  "description": "Mensagem publicada pelo G3 no broker (tópico campus.<tipo>) e consumida por G2, G4 e G5.",
  "type": "object", "required": ["idEvento", "tipo", "versaoContrato", "ocorridoEm", "origem", "objetoId", "dados"],
  "additionalProperties": False, "properties": {
    "idEvento": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"},
    "tipo": {"enum": list(EVENTOS)}, "versaoContrato": {"const": VERSAO}, "ocorridoEm": {"$ref": C + "DataHora"},
    "origem": {"type": "object", "required": ["grupo"], "additionalProperties": False, "properties": {
       "grupo": {"enum": ["G1", "G2", "G3", "G4", "G5"]}, "usuario": {"type": "string"}}},
    "objetoId": {"$ref": C + "Identificador"}, "dados": {"type": "object"}},
  "allOf": [{"if": {"required": ["tipo"], "properties": {"tipo": {"const": t}}},
             "then": {"properties": {"dados": {"type": "object", "additionalProperties": False, **spec}}}} for t, spec in EVENTOS.items()]}
OBJ_REFS = [{"$ref": "edificacao.schema.json"}, {"$ref": "via.schema.json"},
            {"$ref": "ponto-de-interesse.schema.json"}, {"$ref": "area-verde.schema.json"}]
HIST = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + "historico-do-objeto.schema.json",
  "title": "Histórico de versões de um objeto urbano (RF14)",
  "description": "Cada versão é um retrato completo do objeto com período de validade; persistido pelo G2.",
  "type": "object", "required": ["objetoId", "versoes"], "additionalProperties": False, "properties": {
    "objetoId": {"$ref": C + "Identificador"},
    "versoes": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
      "required": ["versao", "validoDe", "alteradoPor", "motivo", "objeto"], "properties": {
        "versao": {"type": "integer", "minimum": 1}, "validoDe": {"$ref": C + "DataHora"},
        "validoAte": {"$ref": C + "DataHora"}, "alteradoPor": {"type": "string", "minLength": 2},
        "motivo": {"type": "string", "minLength": 5}, "objeto": {"oneOf": OBJ_REFS}}}}}}
REL = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + "relatorio-de-validacao.schema.json",
  "title": "Relatório de validação do Campus Domain (RF-06)",
  "description": "Devolvido por validar_documento() e por POST /validacao; o G3 o repassa na própria API.",
  "type": "object", "required": ["valido", "erros"], "additionalProperties": False, "properties": {
    "valido": {"type": "boolean"},
    "erros": {"type": "array", "items": {"type": "object", "required": ["codigo", "regra", "local", "mensagem"],
      "additionalProperties": False, "properties": {
        "codigo": {"type": "string", "pattern": "^G1-[A-Z]{3}-[0-9]{3}$"},
        "regra": {"type": "string", "pattern": "^(INV-[0-9]{2}|SCHEMA)$"},
        "local": {"type": "string", "description": "JSON Pointer do ponto do documento com problema."},
        "mensagem": {"type": "string", "description": "Mensagem em português com os termos do glossário."}}}}}}
for name, s in [("relatorio-de-validacao", REL), ("evento-de-dominio", EVT), ("historico-do-objeto", HIST), ("vocabulario", VOCAB_SCHEMA), ("comum", COMUM), ("edificacao", EDF), ("via", VIA), ("ponto-de-interesse", POI),
                ("area-verde", AV), ("modelo-do-campus", MOD)]:
    dump(f"schemas/json/{name}.schema.json", s)

# ---------------- @context JSON-LD ----------------
CTX = {"@context": {"@version": 1.1,
  "campus": "urn:upm:campus-hig:vocab#", "bldg": "http://www.opengis.net/citygml/building/3.0#",
  "tran": "http://www.opengis.net/citygml/transportation/3.0#",
  "veg": "http://www.opengis.net/citygml/vegetation/3.0#",
  "geo": "http://www.opengis.net/ont/geosparql#", "schema": "https://schema.org/",
  "id": "@id", "tipo": "@type",
  "Edificacao": "campus:Edificacao", "Pavimento": "campus:Pavimento", "Via": "campus:Via",
  "PontoDeInteresse": "campus:PontoDeInteresse", "AreaVerde": "campus:AreaVerde",
  "nome": "schema:name", "numeroMapa": "campus:numeroMapa", "homenageado": "campus:homenageado",
  "localizacao": "campus:localizacao", "categoriaUso": {"@id": "campus:categoriaUso", "@type": "@vocab"},
  "categoria": {"@id": "campus:categoria", "@type": "@vocab"},
  "unidadesOcupantes": {"@id": "campus:unidadeOcupante", "@container": "@set"},
  "pavimentos": {"@id": "campus:possuiPavimento", "@container": "@set"},
  "numero": "campus:numero", "numeroPortaria": "campus:numeroPortaria", "classe": "campus:classeVia", "revestimento": "campus:revestimento",
  "cobertura": "campus:coberturaVegetal", "situacao": "campus:situacao",
  "edificacaoRef": {"@id": "campus:situadoEm", "@type": "@id"},
  "endereco": "schema:address", "logradouro": "schema:streetAddress", "municipio": "schema:addressLocality",
  "uf": "schema:addressRegion", "crs": "campus:crs",
  "geometria": {"@id": "geo:hasGeometry", "@type": "@json"}, "metadados": {"@id": "campus:metadados", "@type": "@json"}}}
dump("schemas/jsonld/context.jsonld", CTX)

# ---------------- exemplos a partir do mapa ----------------
# Âncora aproximada: pixel (700,600) do mapa ≈ (-46.6519, -23.5470) WGS 84; escala 0,28 m/pixel.
t = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
E0, N0 = t.transform(-46.6519, -23.5470)
ESC = 0.28
def p(x, y): return [round(E0 + (x - 700) * ESC, 2), round(N0 - (y - 600) * ESC, 2)]
def box(x1, y1, x2, y2): return {"type": "Polygon", "coordinates": [[p(x1, y1), p(x2, y1), p(x2, y2), p(x1, y2), p(x1, y1)]]}
def poly(pts): return {"type": "Polygon", "coordinates": [[p(*q) for q in pts] + [p(*pts[0])]]}
def line(pts): return {"type": "LineString", "coordinates": [p(*q) for q in pts]}
def pt(x, y): return {"type": "Point", "coordinates": p(x, y)}
U = "urn:upm:campus-hig:"
meta = {"versao": 1, "fonte": "Mapa Campus Higienópolis 2024 (geometria esquemática)"}

PERIM = poly([(120, 455), (590, 75), (1285, 945), (300, 1065)])
ADI = p(0, 1160) + p(2048, 0)
CAMPUS = {"id": U + "campus:higienopolis", "nome": "Campus Higienópolis", "crs": CRS,
          "perimetro": PERIM, "areaDeInteresse": ADI}
ed31 = {"tipo": "Edificacao", "id": U + "edificacao:31", "crs": CRS, "numeroMapa": 31,
  "nome": "Faculdade de Computação e Informática (FCI)", "homenageado": "Ed. Paulo Breda Filho",
  "localizacao": "interna", "categoriaUso": "ensino", "unidadesOcupantes": ["FCI"],
  "situacao": "ativo", "geometria": box(660, 650, 740, 740), "metadados": meta}
ed41 = {"tipo": "Edificacao", "id": U + "edificacao:41", "crs": CRS, "numeroMapa": 41,
  "nome": "Edifício João Calvino", "homenageado": "Ed. João Calvino", "localizacao": "interna",
  "categoriaUso": "administrativo", "unidadesOcupantes": ["Reitoria e Pró-Reitorias"],
  "endereco": {"logradouro": "Rua da Consolação", "numero": "896", "municipio": "São Paulo", "uf": "SP"},
  "situacao": "ativo", "geometria": box(920, 880, 1010, 970),
  "pavimentos": [
     {"id": U + "pavimento:41-0", "numero": 0, "nome": "Térreo", "geometria": box(920, 880, 1010, 970)},
     {"id": U + "pavimento:41-8", "numero": 8, "nome": "8º pavimento", "geometria": box(920, 880, 1010, 970),
      "unidadesOcupantes": ["Coordenadoria Geral de Pós-Graduação Stricto Sensu (PRPG)"]}],
  "metadados": meta}
ed09 = {"tipo": "Edificacao", "id": U + "edificacao:09", "crs": CRS, "numeroMapa": 9,
  "nome": "Faculdade de Arquitetura e Urbanismo (FAU)", "homenageado": "Ed. Cristiano Stockler das Neves",
  "localizacao": "interna", "categoriaUso": "ensino", "unidadesOcupantes": ["FAU"], "situacao": "ativo",
  "geometria": box(410, 270, 510, 370), "metadados": meta}
ed358 = {"tipo": "Edificacao", "id": U + "edificacao:ext-maria-antonia-358", "crs": CRS, "numeroMapa": 358,
  "nome": "Núcleo de Inovação e Tecnologia (NIT) / LPP / Bolsas / UPM Digital", "localizacao": "externa",
  "categoriaUso": "pesquisa", "unidadesOcupantes": ["NIT", "LPP", "Bolsas", "UPM Digital"],
  "endereco": {"logradouro": "Rua Maria Antônia", "numero": "358", "municipio": "São Paulo", "uf": "SP"},
  "situacao": "ativo", "geometria": box(760, 155, 815, 210), "metadados": meta}
ed40 = {"tipo": "Edificacao", "id": U + "edificacao:40", "crs": CRS, "numeroMapa": 40,
  "nome": "Universidade Presbiteriana Mackenzie (UPM)", "homenageado": "Ed. Antônio Bandeira Trajano",
  "localizacao": "interna", "categoriaUso": "ensino", "unidadesOcupantes": ["UPM"], "situacao": "ativo",
  "geometria": box(785, 860, 845, 920), "metadados": meta}
ed40e = {"tipo": "Edificacao", "id": U + "edificacao:ext-maria-borba-40", "crs": CRS, "numeroMapa": 40,
  "nome": "Pós-Graduação Lato Sensu", "homenageado": "Ed. Rev. Alexander Latimer Blackford", "localizacao": "externa",
  "categoriaUso": "ensino", "unidadesOcupantes": ["Pós-Graduação Lato Sensu"],
  "endereco": {"logradouro": "Rua Maria Borba", "numero": "40", "municipio": "São Paulo", "uf": "SP"},
  "situacao": "ativo", "geometria": box(1490, 700, 1580, 770), "metadados": meta}
via_cons = {"tipo": "Via", "id": U + "via:rua-da-consolacao", "crs": CRS, "nome": "Rua da Consolação",
  "classe": "publica", "revestimento": "asfalto", "geometria": line([(280, 1095), (1310, 975)]), "metadados": meta}
via_ita = {"tipo": "Via", "id": U + "via:rua-itambe", "crs": CRS, "nome": "Rua Itambé",
  "classe": "publica", "revestimento": "asfalto", "geometria": line([(95, 440), (575, 50)]), "metadados": meta}
port07 = {"tipo": "PontoDeInteresse", "id": U + "poi:portaria-07", "crs": CRS, "nome": "Portaria 07",
  "categoria": "portaria", "numeroPortaria": 7,
  "endereco": {"logradouro": "Rua da Consolação", "numero": "930", "municipio": "São Paulo", "uf": "SP"},
  "geometria": pt(913, 991), "metadados": meta}
port01 = {"tipo": "PontoDeInteresse", "id": U + "poi:portaria-01", "crs": CRS, "nome": "Portaria 01",
  "categoria": "portaria", "numeroPortaria": 1,
  "endereco": {"logradouro": "Rua Itambé", "numero": "185", "municipio": "São Paulo", "uf": "SP"},
  "geometria": pt(157, 425), "metadados": meta}
achados = {"tipo": "PontoDeInteresse", "id": U + "poi:achados-e-perdidos", "crs": CRS,
  "nome": "Achados e Perdidos", "categoria": "achados-e-perdidos", "edificacaoRef": U + "edificacao:35",
  "geometria": pt(764, 893), "metadados": meta}
av = {"tipo": "AreaVerde", "id": U + "area-verde:bosque-norte", "crs": CRS, "nome": "Bosque do setor norte",
  "cobertura": "arborea", "geometria": box(500, 180, 580, 260), "metadados": meta}
VALID = [ed31, ed41, ed09, ed40, ed358, ed40e, via_cons, via_ita, port07, port01, achados, av]
for o in VALID:
    dump(f"examples/valid/{o['id'].split(':', 3)[-1].replace(':', '-')}.json", o)
modelo = {"versaoContrato": VERSAO, "campus": CAMPUS, "objetos": VALID}
dump("examples/valid/modelo-campus-higienopolis.json", modelo)

def hist_41():
    v1 = copy.deepcopy(ed41); v1["metadados"] = {"versao": 1, "atualizadoEm": "2024-03-01T09:00:00-03:00",
        "alteradoPor": "gestor.suinf", "fonte": meta["fonte"]}
    v1["pavimentos"][1].pop("unidadesOcupantes")
    v2 = copy.deepcopy(ed41); v2["metadados"] = {"versao": 2, "atualizadoEm": "2026-11-25T10:00:00-03:00",
        "alteradoPor": "gestor.suinf", "fonte": meta["fonte"]}
    return {"objetoId": ed41["id"], "versoes": [
      {"versao": 1, "validoDe": "2024-03-01T09:00:00-03:00", "validoAte": "2026-11-25T10:00:00-03:00",
       "alteradoPor": "gestor.suinf", "motivo": "Carga inicial a partir do mapa do campus 2024", "objeto": v1},
      {"versao": 2, "validoDe": "2026-11-25T10:00:00-03:00", "alteradoPor": "gestor.suinf",
       "motivo": "Registro da Coordenadoria Geral de Pós-Graduação no 8º pavimento", "objeto": v2}]}
dump("examples/valid/historico-edificacao-41.json", hist_41())
EV = lambda n, t, oid, dados, quando: {"idEvento": f"0b6f1c2e-6d1a-4c47-9b1e-0000000000{n:02d}", "tipo": t,
    "versaoContrato": VERSAO, "ocorridoEm": quando, "origem": {"grupo": "G3", "usuario": "gestor.suinf"},
    "objetoId": oid, "dados": dados}
dump("examples/valid/evento-objeto-cadastrado-31.json", EV(1, "ObjetoUrbanoCadastrado", ed31["id"],
     {"tipoObjeto": "Edificacao", "versao": 1}, "2026-11-25T10:05:00-03:00"))
dump("examples/valid/evento-pavimento-adicionado-41.json", EV(2, "PavimentoAdicionado", ed41["id"],
     {"pavimentoId": U + "pavimento:41-8", "numero": 8}, "2026-11-25T10:06:00-03:00"))
dump("examples/valid/evento-geometria-atualizada-bosque.json", EV(3, "GeometriaAtualizada", av["id"],
     {"versaoAnterior": 1, "versaoNova": 2}, "2026-11-25T10:07:00-03:00"))

# Inválidos: cada um viola exatamente uma regra (código esperado em _esperado)
def inv(nome, base, mut, codigo, regra, colecao=False):
    o = copy.deepcopy(base); mut(o)
    doc = {"versaoContrato": VERSAO, "campus": CAMPUS, "objetos": VALID + [o]} if colecao else o
    doc_out = {"_esperado": {"codigo": codigo, "regra": regra}, "documento": doc}
    dump(f"examples/invalid/{nome}.json", doc_out)
def s(k, v): return lambda o: o.__setitem__(k, v)
inv("inv-02-fora-area-de-interesse", ed358, lambda o: (o.update(id=U+"edificacao:ext-teste-999", numeroMapa=999,
    endereco={"logradouro": "Rua de Teste", "numero": "999"}),
    o.__setitem__("geometria", box(3000, 3000, 3100, 3100))), "G1-ESP-002", "INV-02", True)
inv("inv-03-poligono-autointersecao", ed31, s("geometria", poly([(660, 650), (740, 740), (740, 650), (660, 740)])),
    "G1-GEO-003", "INV-03")
inv("inv-03b-anel-nao-fechado", ed31, lambda o: o["geometria"]["coordinates"][0].pop(), "G1-GEO-003", "INV-03")
inv("inv-04-pavimento-fora-da-edificacao", ed41, lambda o: o["pavimentos"][1].__setitem__("geometria",
    box(1000, 880, 1090, 970)), "G1-AGR-004", "INV-04")
inv("inv-05-numero-pavimento-duplicado", ed41, lambda o: o["pavimentos"][0].__setitem__("numero", 8),
    "G1-AGR-005", "INV-05")
inv("inv-06-via-atravessa-edificacao", via_cons, lambda o: o.update(id=U+"via:passagem-teste", nome="Passagem de teste",
    classe="interna", geometria=line([(900, 920), (1030, 930)])), "G1-ESP-006", "INV-06", True)
inv("inv-07-poi-sem-categoria", achados, lambda o: o.pop("categoria"), "G1-SCH-001", "INV-07")
inv("inv-08-area-verde-sobre-edificacao", av, lambda o: o.update(id=U+"area-verde:jardim-teste",
    geometria=box(700, 700, 780, 780)), "G1-ESP-008", "INV-08", True)
inv("inv-09-categoria-fora-do-vocabulario", ed31, s("categoriaUso", "laboratorio"), "G1-SCH-001", "INV-09")
inv("inv-10-crs-diferente", ed31, s("crs", "EPSG:4326"), "G1-SCH-001", "INV-10")
inv("inv-11-numero-mapa-duplicado", ed09, lambda o: o.update(id=U+"edificacao:09-bis"), "G1-ESP-011", "INV-11", True)
inv("inv-12-interna-fora-do-perimetro", ed358, lambda o: (o.update(id=U+"edificacao:900", numeroMapa=900,
    localizacao="interna")), "G1-ESP-012", "INV-12", True)
inv("inv-13-portaria-fora-do-perimetro", port07, lambda o: o.update(id=U+"poi:portaria-99", numeroPortaria=99,
    geometria=pt(913, 1060)), "G1-ESP-013", "INV-13", True)
inv("inv-15-externa-numero-difere-do-endereco", ed358, s("numeroMapa", 359), "G1-AGR-015", "INV-15")
h = hist_41(); h["versoes"][1]["versao"] = 3
dump("examples/invalid/inv-16-historico-com-lacuna-de-versao.json",
     {"_esperado": {"codigo": "G1-HIS-016", "regra": "INV-16"}, "documento": h})
dump("examples/invalid/inv-17-evento-salta-versao.json", {"_esperado": {"codigo": "G1-EVT-017", "regra": "INV-17"},
     "documento": EV(4, "GeometriaAtualizada", av["id"], {"versaoAnterior": 1, "versaoNova": 3}, "2026-11-25T10:08:00-03:00")})
inv("inv-14-externa-sem-endereco", ed358, lambda o: o.pop("endereco"), "G1-SCH-001", "INV-14")
print("contrato", VERSAO, "gerado; origem UTM", round(E0, 1), round(N0, 1))
