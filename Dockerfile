FROM python:3.9-slim

# Ferramentas para diagnóstico e healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates iproute2 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Documenta a porta
EXPOSE 5000

# Healthcheck: tenta acessar a rota de saúde
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:5000/health || exit 1

# Inicia o app (garanta host 0.0.0.0 e port 5000 no app.py)
CMD ["python", "app.py"]