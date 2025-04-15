# Usa la imagen base de Python 3.12-slim (versión genérica para evitar cambios innecesarios)
FROM python:3.12-slim as base

WORKDIR /app

# Instala dependencias del sistema (si necesitas alguna, ej: libpq para PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements.txt primero (para cachear la instalación)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# --- Etapa para FastAPI ---
FROM base as fastapi
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  # Sin --reload

# --- Etapa para Celery ---
FROM base as celery
CMD ["celery", "-A", "config.Celery.celery_worker.celery_app", "worker", "--loglevel=info", "--concurrency=1", "--pool=solo"]