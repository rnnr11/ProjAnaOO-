
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/cache

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=10001:10001 main.py .
COPY pyproject.toml .
COPY --chown=10001:10001 src/ ./src/
RUN pip install --no-cache-dir --no-deps .

USER 10001:10001

ENTRYPOINT ["python", "-B", "-m", "agente"]
