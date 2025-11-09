# ---------- Stage 1: Builder ----------
    FROM python:3.13-slim AS builder

    WORKDIR /app
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
    
    RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && \
        rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt pyproject.toml ./
    
    RUN python -m venv /opt/venv \
     && . /opt/venv/bin/activate \
     && pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir
    
    COPY app/ ./app/
    COPY config/ ./config/
    
    # ---------- Stage 2: Runtime ----------
    FROM python:3.13-slim
    
    WORKDIR /app
    COPY --from=builder /opt/venv /opt/venv
    ENV PATH="/opt/venv/bin:$PATH"
    
    COPY --from=builder /app/app ./app
    COPY --from=builder /app/config ./config
    
    RUN mkdir -p /app/logs && chmod -R 777 /app/logs \
     && useradd -u 1001 -m appuser && chown -R appuser /app
    
    USER appuser
    EXPOSE 8000
    
    CMD ["uvicorn", "app.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
    