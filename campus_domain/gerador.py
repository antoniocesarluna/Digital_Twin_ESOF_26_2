"""Gerador de dados sintéticos do campus (RF-13/RF-14), com semente reproduzível.
Edificações em grade dentro do perímetro, sem sobreposição; modo inválido controlado."""
import copy
import random

from shapely.geometry import box, shape


def gerar_campus(modelo_base: dict, n: int = 20, semente: int = 42, violar: str | None = None) -> dict:
    rnd = random.Random(semente)
    m = copy.deepcopy(modelo_base)
    perim = shape(m["campus"]["perimetro"])
    ocupado = [shape(o["geometria"]).buffer(2) for o in m["objetos"] if o["geometria"]["type"] != "Point"]
    minx, miny, maxx, maxy = perim.bounds
    usados = {o["numeroMapa"] for o in m["objetos"] if o["tipo"] == "Edificacao"}
    num, tent = 500, 0
    while n and tent < 5000:
        tent += 1
        w, h = rnd.uniform(12, 30), rnd.uniform(12, 30)
        x, y = rnd.uniform(minx, maxx - w), rnd.uniform(miny, maxy - h)
        b = box(x, y, x + w, y + h)
        if not perim.buffer(-1).covers(b) or any(b.intersects(o) for o in ocupado):
            continue
        while num in usados: num += 1
        usados.add(num); ocupado.append(b.buffer(2))
        coords = [[round(a, 2), round(c, 2)] for a, c in b.exterior.coords]
        m["objetos"].append({"tipo": "Edificacao", "id": f"urn:upm:campus-hig:edificacao:{num}", "crs": "EPSG:31983",
            "numeroMapa": num, "nome": f"Edificação sintética {num}", "localizacao": "interna",
            "categoriaUso": rnd.choice(["ensino", "pesquisa", "administrativo"]), "situacao": "planejado",
            "geometria": {"type": "Polygon", "coordinates": [coords]}})
        n -= 1
    if violar == "INV-11":   # número do mapa duplicado
        m["objetos"][-1]["numeroMapa"] = m["objetos"][0]["numeroMapa"]
    elif violar == "INV-08": # área verde sobre edificação
        alvo = m["objetos"][-1]["geometria"]
        m["objetos"].append({"tipo": "AreaVerde", "id": "urn:upm:campus-hig:area-verde:sintetica", "crs": "EPSG:31983",
            "nome": "Área verde sintética", "cobertura": "gramado", "geometria": copy.deepcopy(alvo)})
    return m
