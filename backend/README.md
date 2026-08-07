# ZoPic Studio - Backend & IA

Ce dossier contient le cœur de l'application ZoPic Studio.

## Technologies Clés
- **FastAPI** : Framework web asynchrone haute performance.
- **SQLAlchemy & Alembic** : ORM et gestion des migrations (PostgreSQL/SQLite).
- **ARQ & Redis** : Files d'attente pour le traitement asynchrone (filigranes, statistiques).
- **Qdrant** : Base de données vectorielle pour la recherche par visage (embeddings générés par `worker_ai`).
- **MinIO/S3** : Stockage des photos originales et filigranées.

## Démarrage Rapide

Assurez-vous d'avoir Python 3.10+ et le gestionnaire `uv` installé.

1. Installez les dépendances :
   ```bash
   uv sync
   ```
2. Configurez les variables d'environnement (`cp .env.example .env`).
3. Lancez les migrations :
   ```bash
   uv run alembic upgrade head
   ```
4. Démarrez le serveur de développement :
   ```bash
   uv run uvicorn app.main:app --reload
   ```

Pour la documentation détaillée, consultez le dossier `/docs` à la racine du projet.
