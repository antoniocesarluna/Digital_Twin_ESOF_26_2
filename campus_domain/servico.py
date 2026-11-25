"""Serviço HTTP do Campus Domain (RNF10 / ADR-010): publica vocabulários e schemas para o G5,
fixtures para todos os grupos e validação/conversão para o G3. Somente biblioteca padrão.
Execução: python -m campus_domain.servico --porta 8001   (contrato: openapi/campus-domain.openapi.json)"""
import argparse
import json
import logging
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import __version__
from .gerador import gerar_campus
from .mapeamento import de_dict
from .serializacao.geojson import de_geojson, para_geojson
from .serializacao.gml import para_gml
from .validacao import validar_documento

RAIZ = pathlib.Path(__file__).resolve().parents[1]
VOCAB = RAIZ / "schemas" / "vocab"; SCHEMAS = RAIZ / "schemas" / "json"
FIXTURE = RAIZ / "examples" / "valid" / "modelo-campus-higienopolis.json"

def _objetos(corpo):
    objs = corpo["objetos"] if isinstance(corpo, dict) and "objetos" in corpo else (corpo if isinstance(corpo, list) else [corpo])
    return [{k: v for k, v in o.items() if k != "metadados"} for o in objs]

class Handler(BaseHTTPRequestHandler):
    server_version = f"campus-domain/{__version__}"
    def log_message(self, fmt, *args): logging.getLogger("campus_domain.servico").info(fmt % args)

    def _enviar(self, status, corpo, tipo="application/json; charset=utf-8"):
        dados = corpo if isinstance(corpo, bytes) else (corpo.encode("utf-8") if isinstance(corpo, str)
                                                         else json.dumps(corpo, ensure_ascii=False).encode("utf-8"))
        self.send_response(status)
        self.send_header("Content-Type", tipo); self.send_header("Content-Length", str(len(dados)))
        self.send_header("Access-Control-Allow-Origin", "*")           # G5 (Leaflet) chama do navegador
        self.send_header("X-Contrato-Versao", __version__)
        self.end_headers(); self.wfile.write(dados)

    def _arquivo(self, caminho: pathlib.Path):
        if caminho.is_file() and caminho.resolve().parent in (VOCAB.resolve(), SCHEMAS.resolve()):
            return self._enviar(200, caminho.read_bytes())
        return self._enviar(404, {"erro": "recurso não encontrado"})

    def do_OPTIONS(self):
        self.send_response(204)
        for h, v in (("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                     ("Access-Control-Allow-Headers", "Content-Type")):
            self.send_header(h, v)
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path); partes = [p for p in u.path.split("/") if p]
        if partes == ["saude"]: return self._enviar(200, {"status": "ok", "versaoContrato": __version__})
        if partes == ["vocabularios"]: return self._arquivo(VOCAB / "index.json")
        if len(partes) == 2 and partes[0] == "vocabularios": return self._arquivo(VOCAB / f"{partes[1]}.json")
        if len(partes) == 2 and partes[0] == "schemas": return self._arquivo(SCHEMAS / f"{partes[1]}.schema.json")
        if partes == ["fixtures", "campus"]:
            q = parse_qs(u.query); modelo = json.loads(FIXTURE.read_text("utf-8"))
            n = int(q.get("sinteticos", ["0"])[0])
            if n: modelo = gerar_campus(modelo, n=min(n, 200), semente=int(q.get("semente", ["42"])[0]))
            if q.get("formato", ["contrato"])[0] == "geojson": return self._enviar(200, para_geojson(modelo), "application/geo+json")
            return self._enviar(200, modelo)
        return self._enviar(404, {"erro": "rota não encontrada"})

    def do_POST(self):
        try:
            corpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"null")
        except json.JSONDecodeError as e:
            return self._enviar(400, {"erro": f"JSON inválido: {e.msg}"})
        rota = urlparse(self.path).path.rstrip("/")
        try:
            if rota == "/validacao":
                rel = validar_documento(corpo); return self._enviar(200 if rel.valido else 422, rel.para_dict())
            if rota == "/conversao/geojson": return self._enviar(200, para_geojson(corpo), "application/geo+json")
            if rota == "/conversao/contrato": return self._enviar(200, {"documentos": de_geojson(corpo)})
            if rota == "/exportacao/citygml":
                return self._enviar(200, para_gml([de_dict(o) for o in _objetos(corpo)]), "application/gml+xml; charset=utf-8")
        except (KeyError, TypeError, ValueError) as e:
            return self._enviar(400, {"erro": f"documento fora do contrato: {e}"})
        return self._enviar(404, {"erro": "rota não encontrada"})

def criar_servidor(porta: int = 8001, host: str = "0.0.0.0") -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, porta), Handler)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("--porta", type=int, default=8001)
    a = ap.parse_args(); logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(f"Campus Domain {__version__} em http://0.0.0.0:{a.porta}"); criar_servidor(a.porta).serve_forever()
