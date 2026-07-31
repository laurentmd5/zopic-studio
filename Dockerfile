# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Setup uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies in the system environment
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
