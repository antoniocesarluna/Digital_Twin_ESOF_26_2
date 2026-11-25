# Serviço do Campus Domain (G1) — RNF07/RNF10
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY campus_domain/ campus_domain/
COPY schemas/ schemas/
COPY examples/ examples/
COPY openapi/ openapi/
EXPOSE 8001
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/saude')"
CMD ["python", "-m", "campus_domain.servico", "--porta", "8001"]
