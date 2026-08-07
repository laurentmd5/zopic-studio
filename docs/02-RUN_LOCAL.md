# Lancer ZoPic Studio en Local

Ce guide explique comment lancer la stack complète ZoPic Studio (Backend + AI Worker + Frontends) sur votre machine de développement.

## Prérequis
- [Docker & Docker Compose](https://www.docker.com/)
- [Python 3.10+](https://www.python.org/) et `uv` (Gestionnaire de paquets)
- [Node.js 20+](https://nodejs.org/)

---

## Étape 1 : Démarrer les Services Tiers (Docker)

Le backend a besoin de MinIO (S3), Redis (Tasks), et Qdrant (IA).
```bash
docker compose up -d minio redis qdrant
```

Initialisez la base de données et Qdrant :
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python scripts/init_qdrant.py
```

## Étape 2 : Lancer le Backend FastAPI

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
L'API est accessible sur `http://localhost:8000/docs`.

## Étape 3 : Lancer le Worker IA (Reconnaissance Faciale)

```bash
cd backend/worker_ai
uv sync
uv run python app/worker.py
```

## Étape 4 : Lancer les Frontends

Ouvrez deux nouveaux terminaux.

**Portail Web (Photographes) :**
```bash
cd frontend-web
npm install
npm run dev # -> http://localhost:5173
```

**PWA Client (Athlètes) :**
```bash
cd frontend-client
npm install
npm run dev # -> http://localhost:5174
```
