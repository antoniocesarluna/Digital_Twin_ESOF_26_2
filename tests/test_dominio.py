import ast, pathlib, pytest
from campus_domain.dominio import (RegraDeDominioViolada, Identificador, NumeroMapa, Geometria, Pavimento,
                                   Edificacao, Endereco, PontoDeInteresse, PavimentoAdicionado)
Q = ((((0, 0), (10, 0), (10, 10), (0, 10), (0, 0)),))
def edf(**kw):
    base = dict(id=Identificador("urn:upm:campus-hig:edificacao:31"), numero_mapa=NumeroMapa(31), nome="FCI",
                localizacao="interna", categoria_uso="ensino", situacao="ativo", geometria=Geometria("Polygon", Q))
    base.update(kw); return Edificacao.criar(**base)

def test_inv01_identificador_fora_do_padrao():
    with pytest.raises(RegraDeDominioViolada, match="INV-01"): Identificador("predio-31")
def test_inv11_numero_mapa_fora_da_faixa():
    with pytest.raises(RegraDeDominioViolada, match="INV-11"): NumeroMapa(0)
def test_inv10_crs_diferente():
    with pytest.raises(RegraDeDominioViolada, match="INV-10"): Geometria("Polygon", Q, "EPSG:4326")
def test_inv14_externa_sem_endereco():
    with pytest.raises(RegraDeDominioViolada, match="INV-14"): edf(localizacao="externa")
def test_externa_com_endereco_ok():
    e = edf(localizacao="externa", numero_mapa=NumeroMapa(358), endereco=Endereco("Rua Maria Antônia", "358"))
    assert e.endereco.numero == "358"
def test_inv15_externa_numero_difere_do_endereco():
    with pytest.raises(RegraDeDominioViolada, match="INV-15"):
        edf(localizacao="externa", endereco=Endereco("Rua Maria Antônia", "358"))
def test_inv05_pavimento_duplicado_e_evento():
    e = edf(); g = Geometria("Polygon", Q)
    ev = e.adicionar_pavimento(Pavimento(Identificador("urn:upm:campus-hig:pavimento:31-1"), 1, "1º", g))
    assert isinstance(ev, PavimentoAdicionado) and ev.numero == 1
    with pytest.raises(RegraDeDominioViolada, match="INV-05"):
        e.adicionar_pavimento(Pavimento(Identificador("urn:upm:campus-hig:pavimento:31-1b"), 1, "1º", g))
def test_pavimentos_ordenados_e_imutaveis_por_fora():
    e = edf(); g = Geometria("Polygon", Q)
    for n in (2, 0, 1): e.adicionar_pavimento(Pavimento(Identificador(f"urn:upm:campus-hig:pavimento:31-{n}"), n, str(n), g))
    assert [p.numero for p in e.pavimentos] == [0, 1, 2] and isinstance(e.pavimentos, tuple)
def test_value_objects_igualdade_por_valor():
    assert Endereco("Rua Itambé", "185") == Endereco("Rua Itambé", "185")
def test_inv07_portaria_sem_endereco():
    with pytest.raises(RegraDeDominioViolada, match="INV-07"):
        PontoDeInteresse.criar(id=Identificador("urn:upm:campus-hig:poi:portaria-01"), nome="Portaria 01",
                               categoria="portaria", geometria=Geometria("Point", (0, 0)), numero_portaria=1)

def test_rnf01_dominio_sem_dependencia_de_infraestrutura():
    fonte = (pathlib.Path(__file__).resolve().parents[1] / "campus_domain/dominio.py").read_text("utf-8")
    mods = {n.names[0].name.split(".")[0] for n in ast.walk(ast.parse(fonte)) if isinstance(n, ast.Import)}
    mods |= {n.module.split(".")[0] for n in ast.walk(ast.parse(fonte)) if isinstance(n, ast.ImportFrom) and n.module}
    assert not mods & {"json", "xml", "lxml", "sqlite3", "psycopg", "requests", "http", "urllib"}
