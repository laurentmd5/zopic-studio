FROM python:3.11-slim

# Installer les dÃ©pendances systÃ¨me requises par OpenCV et InsightFace
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copier les fichiers du projet
COPY pyproject.toml .

# Installer les dÃ©pendances
RUN uv sync --frozen --no-cache || uv sync --no-cache

# Copier le reste du code
COPY . .

# Par dÃ©faut on dÃ©marre l'API
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
