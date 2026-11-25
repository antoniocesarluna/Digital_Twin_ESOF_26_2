import json, pathlib, pytest
RAIZ = pathlib.Path(__file__).resolve().parents[1]
def carregar(rel): return json.loads((RAIZ / rel).read_text("utf-8"))
@pytest.fixture
def modelo(): return carregar("examples/valid/modelo-campus-higienopolis.json")
