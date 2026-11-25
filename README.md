# Campus Domain — Grupo 1 (Gêmeo Digital Urbano do Campus)
Contrato v0.1.0 (Published Language) e biblioteca de validação/serialização.

    pip install -r requirements.txt
    python tools/build_contract.py   # regenera schemas e exemplos
    pytest -q --cov=campus_domain

Uso pelo Grupo 3:

    from campus_domain import validar, validar_modelo
    rel = validar(documento)          # objeto isolado
    if not rel.valido: return 422, rel.para_dict()

Geometrias dos exemplos são esquemáticas (mapa ilustrativo, sem georreferenciamento).
