# Stage 1 — Builder

FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY app/ ./app/
COPY config/ ./config/


# Stage 2 — Runtime

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app/ ./app/
COPY config/ ./config/

# Create logs directory and give permissions
RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]