# syntax=docker/dockerfile:1

# Build Stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Setup uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies without dev dependencies
RUN uv sync --frozen --no-dev --no-cache

# Runtime Stage
FROM python:3.13-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

EXPOSE 8000

# Run the application directly using the virtual environment
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
