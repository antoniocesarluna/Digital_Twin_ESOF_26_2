"""Compara o contrato atual com o de uma tag e exige o incremento de versão correto (política da seção 6.1).
uso: python tools/detectar_breaking_change.py --base g1-v0.1.0"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
MAJOR, MINOR, PATCH = 3, 2, 1
NOME = {MAJOR: "MAJOR", MINOR: "MINOR", PATCH: "PATCH", 0: "nenhuma"}

def comparar(old, new, caminho="#"):
    """Devolve [(nível, descrição)] das diferenças entre dois JSON Schemas."""
    achados = []
    if not isinstance(old, dict) or not isinstance(new, dict):
        return [] if old == new else [(MAJOR, f"{caminho}: definição alterada")]
    for chave in ("type", "const", "$ref", "pattern"):
        if old.get(chave) != new.get(chave) and chave in old:
            achados.append((MAJOR, f"{caminho}: '{chave}' alterado de {old.get(chave)!r} para {new.get(chave)!r}"))
    if "enum" in old or "enum" in new:
        a, b = set(map(json.dumps, old.get("enum", []))), set(map(json.dumps, new.get("enum", [])))
        if a - b: achados.append((MAJOR, f"{caminho}: valores removidos do enum {sorted(a - b)}"))
        if b - a: achados.append((MINOR, f"{caminho}: valores novos no enum {sorted(b - a)}"))
    novos_req = set(new.get("required", [])) - set(old.get("required", []))
    if novos_req: achados.append((MAJOR, f"{caminho}: campos passaram a ser obrigatórios {sorted(novos_req)}"))
    if old.get("additionalProperties", True) is not False and new.get("additionalProperties", True) is False:
        achados.append((MAJOR, f"{caminho}: passou a rejeitar campos adicionais"))
    for grupo in ("properties", "$defs"):
        po, pn = old.get(grupo, {}), new.get(grupo, {})
        for k in po.keys() - pn.keys(): achados.append((MAJOR, f"{caminho}/{grupo}/{k}: removido"))
        for k in pn.keys() - po.keys(): achados.append((MINOR, f"{caminho}/{grupo}/{k}: adicionado"))
        for k in po.keys() & pn.keys(): achados += comparar(po[k], pn[k], f"{caminho}/{grupo}/{k}")
    if "items" in old and "items" in new: achados += comparar(old["items"], new["items"], caminho + "/items")
    return achados

def _versao(texto): return tuple(int(x) for x in re.search(r'VERSAO = "(\d+)\.(\d+)\.(\d+)"', texto).groups())

def versao_suficiente(antiga, nova, nivel):
    if nivel == MAJOR: return nova[0] > antiga[0] or (antiga[0] == 0 and nova[:2] > antiga[:2])
    if nivel == MINOR: return nova[:2] > antiga[:2]
    if nivel == PATCH: return nova > antiga
    return True

def _git(*args): return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base", required=True); base = ap.parse_args().base
    antigos = set(_git("ls-tree", "-r", "--name-only", base, "schemas").split())
    atuais = {str(p.relative_to(RAIZ)) for p in (RAIZ / "schemas").rglob("*") if p.is_file()}
    achados = [(MAJOR, f"{p}: arquivo removido do contrato") for p in sorted(antigos - atuais)]
    achados += [(MINOR, f"{p}: arquivo novo") for p in sorted(atuais - antigos)]
    for p in sorted(antigos & atuais):
        if p.startswith("schemas/json/"):
            velho = json.loads(_git("show", f"{base}:{p}")); novo = json.loads((RAIZ / p).read_text("utf-8"))
            velho.pop("$id", None); novo.pop("$id", None)
            achados += [(n, f"{p} {d}") for n, d in comparar(velho, novo)]
    antiga = _versao(_git("show", f"{base}:tools/build_contract.py")); nova = _versao((RAIZ / "tools/build_contract.py").read_text("utf-8"))
    nivel = max((n for n, _ in achados), default=0)
    for n, d in sorted(achados, reverse=True): print(f"[{NOME[n]}] {d}")
    ok = versao_suficiente(antiga, nova, nivel)
    print(f"\nMudança exigida: {NOME[nivel]} | versão {'.'.join(map(str, antiga))} -> {'.'.join(map(str, nova))} | {'OK' if ok else 'BLOQUEADO'}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
