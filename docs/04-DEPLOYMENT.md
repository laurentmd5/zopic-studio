# Guide de Déploiement CI/CD

ZoPic Studio utilise **Jenkins** pour l'intégration et le déploiement continu.
Le pipeline est défini dans le fichier `Jenkinsfile` à la racine du projet.

## Architecture du Déploiement
Le projet est déployé sous forme de conteneurs Docker via `docker-compose.yml`.
L'infrastructure cible contient :
- Nginx (Reverse Proxy)
- Backend (FastAPI)
- Worker IA (ARQ/Python)
- Frontends (Serveur statique / SSR)
- Base de données (PostgreSQL), Redis, MinIO, Qdrant.

## Étapes du Pipeline (Jenkinsfile)
1. **Clone** : Récupération du code source.
2. **Linting (Parallèle)** : `ruff check` (Backend) et `eslint` (Frontends).
3. **Tests (Parallèle)** : `pytest` (Backend) et `vitest` (Frontends).
4. **Build Docker (Parallèle)** : Construction des 4 images Docker.
5. **Security Scan** : Scan statique des images générées avec **Trivy**.
6. **Deploy** : 
   - Copie du `docker-compose.yml` et scripts (ex: `init_qdrant.py`).
   - `docker compose down && docker compose up -d`.
   - Migration de base de données (`alembic upgrade head`).
7. **E2E & DAST** : Tests fonctionnels (Playwright) et sécurité dynamique (OWASP ZAP).

## Variables requises sur le serveur Jenkins
Assurez-vous que les dépendances suivantes sont installées sur l'agent Jenkins :
- Docker Engine
- `uv` (installé dynamiquement par le script si manquant)
- `trivy` pour l'étape de scan de sécurité.
