# syntax=docker/dockerfile:1

# Build Stage
FROM python:3.11-slim AS builder

# Installer les dépendances système requises
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copier les fichiers du projet
COPY pyproject.toml ./

# Installer les dépendances
RUN uv sync --frozen --no-dev --no-cache || uv sync --no-dev --no-cache

# Runtime Stage
FROM python:3.11-slim

# Installer uniquement les dépendances d'exécution (OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copier le reste du code
COPY . .

# Par défaut on démarre l'API
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
