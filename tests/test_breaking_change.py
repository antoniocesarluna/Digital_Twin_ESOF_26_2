"""O detector de mudanças incompatíveis aplica a política de versionamento da seção 6.1."""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("bc", pathlib.Path(__file__).resolve().parents[1] / "tools/detectar_breaking_change.py")
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
BASE = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}, "c": {"enum": ["x", "y"]}}}

def nivel(novo): return max((n for n, _ in bc.comparar(BASE, novo)), default=0)

def test_campo_opcional_novo_e_minor():
    assert nivel({**BASE, "properties": {**BASE["properties"], "b": {"type": "integer"}}}) == bc.MINOR
def test_campo_removido_e_major():
    assert nivel({**BASE, "properties": {"a": {"type": "string"}}}) == bc.MAJOR
def test_campo_obrigatorio_novo_e_major():
    assert nivel({**BASE, "required": ["a", "c"]}) == bc.MAJOR
def test_valor_de_enum_removido_e_major_e_adicionado_e_minor():
    assert nivel({**BASE, "properties": {**BASE["properties"], "c": {"enum": ["x"]}}}) == bc.MAJOR
    assert nivel({**BASE, "properties": {**BASE["properties"], "c": {"enum": ["x", "y", "z"]}}}) == bc.MINOR
def test_regra_de_versao():
    assert bc.versao_suficiente((0, 1, 0), (1, 0, 0), bc.MAJOR)
    assert not bc.versao_suficiente((1, 0, 0), (1, 1, 0), bc.MAJOR)
    assert bc.versao_suficiente((1, 0, 0), (1, 1, 0), bc.MINOR)
