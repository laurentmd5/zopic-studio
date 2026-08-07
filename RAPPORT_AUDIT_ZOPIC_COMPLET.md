# Rapport d'audit complet — ZoPic Studio

## 1. Contexte et portée

Ce document présente un audit complet du projet ZoPic Studio, monorepo composé de plusieurs sous-projets :
- `backend/` : API FastAPI, traitement asynchrone, gestion métier, stockage et biométrie.
- `backend/worker_ai/` : service IA dédié à la reconnaissance faciale et à l'orchestration Qdrant.
- `frontend-web/` : portail React/Vite pour photographes.
- `frontend-client/` : PWA React/Vite mobile-first pour athlètes.
- `docs/` : guides de configuration, exécution locale, API et déploiement.
- `tests-e2e/` : tests Playwright et configuration E2E.
- `zopic_photos_app/` : projet Flutter distinct et probablement non connecté.

L'audit couvre l'architecture, les dépendances, la sécurité, les risques, la qualité du code et les pratiques CI/CD.

## 2. Architecture globale

### 2.1 Structure

- Monorepo multi-stack regroupant backend Python, frontends React et un microservice IA.
- `docker-compose.yml` orchestre PostgreSQL, Redis, MinIO, Qdrant, backend, worker IA et deux frontends.
- Le backend expose l'API principale sous `/api/v1` et inclut une route SSR pour les profils publics d'athlètes.
- Le worker IA expose un service HTTP distinct sur le port `8001`.

### 2.2 Principales technologies

- Backend : Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Redis/ARQ, SlowAPI, Qdrant, MinIO/S3.
- IA : FastAPI, InsightFace, ONNX Runtime, OpenCV-headless, Qdrant.
- Frontends : React 19, TypeScript 6, Vite 8, ESLint, Vitest, Playwright.
- CI/CD : Jenkins, Docker, Trivy, OWASP ZAP, tests parallèles.

## 3. Backend

### 3.1 Configuration et dépendances

- `backend/pyproject.toml` cible Python `>=3.13`.
- Dépendances notables : `fastapi[standard]`, `sqlalchemy`, `pydantic`, `qdrant-client`, `redis`, `arq`, `slowapi`, `python-multipart`, `aioboto3`.
- Groupe `dev` exposé : `pytest`, `pytest-asyncio`, `ruff`, `coverage`.
- `backend/.env.example` définit les variables attendues.

### 3.2 Gestion des variables d'environnement

- `app/core/config.py` utilise `pydantic-settings` et charge `.env`.
- Validation : en production, `PAYMENT_SIMULATION_MODE=False` exige un `PAYMENT_WEBHOOK_SECRET` non par défaut.
- Risques : valeurs par défaut sensibles (`SECRET_KEY`, `PAYMENT_WEBHOOK_SECRET`) doivent être changées en production.

### 3.3 Authentification et sécurité

- Authentification basée sur OTP SMS et JWT.
- Route `POST /api/v1/auth/request-otp` limitée à `3/minute`.
- Route `POST /api/v1/auth/verify` limitée à `5/minute`.
- `slowapi` gère le rate limiting global.
- L'utilisation d'un callback interne avec `secret` en query string (`/orders/{order_id}/archives/{archive_id}/callback`) est fonctionnelle mais présente un risk d’exfiltration si les logs HTTP ou URL sont exposés.

### 3.4 Stockage et ressources

- `storage` expose des URL pré-signées pour upload/download S3.
- `face_recognition` proxie un selfie au service IA et enrichit la réponse avec des URLs présignées.
- L’API limite le poids du selfie à `10 MB`.
- `backend/app/modules/competitions/models.py` utilise un champ JSON flexible pour `settings` et `packs`, ce qui facilite l’évolution mais peut masquer des schémas métier critiques.

### 3.5 IA et biométrie

- La reconnaissance faciale passe par `backend/worker_ai`.
- `backend/app/modules/face_recognition/router.py` enregistre des logs d'audit pour chaque recherche et oubli biométrique.
- Le service IA réalise les opérations `/search` et `/forget` sur des collections Qdrant nommées `faces_v1_{competition_id}`.
- Le worker IA supporte également des tâches cron ARQ pour :
  - traitement des événements de paiement,
  - mise à jour des statistiques athlètes,
  - nettoyage biométrique des compétitions archivées.

### 3.6 Architecture asynchrone

- `backend/app/worker.py` définit des tâches ARQ et un outbox pattern.
- L’approche combine base de données et Redis pour la fiabilité des événements.
- L’exécution `arq_cleanup_biometrics` supprime des collections Qdrant anciennes.

### 3.7 Observations de sécurité

- Bonne pratique : utilisation de `hmac.compare_digest` pour webhook PayDunya.
- À améliorer : ne pas utiliser de secret sensible dans l’URL de callback.
- La configuration CORS est dynamique et autorise local dev fallback ; en production, la whitelist doit être stricte.

## 4. Worker IA (`backend/worker_ai`)

### 4.1 Configuration

- `backend/worker_ai/pyproject.toml` cible Python `>=3.11`, ce qui crée un écart de version entre le backend principal et le worker.
- Dépendances IA : `insightface`, `onnxruntime`, `opencv-python-headless`, `qdrant-client`, `httpx` implicite via proxy.

### 4.2 Docker

- Dockerfile multi-stage avec Python 3.11 et dépendances système OpenCV.
- Le build tente un `uv sync --frozen`, puis un fallback sans `--frozen`; cela suggère que `uv.lock` peut être manquant ou non strictement maintenu.

### 4.3 Points de robustesse

- Le worker expose une API HTTP publique (`/search`, `/forget`).
- Il n’y a pas de mécanisme d’authentification sur ces endpoints dans le code lu, donc l’invocation interne doit être protégée au niveau réseau ou via un proxy.
- La recherche Qdrant utilise un seuil de similarité fixe `0.85`; la configuration devrait idéalement être paramétrable.

## 5. Frontends

### 5.1 `frontend-web`

- React 19, TypeScript 6, Vite 8.
- Usage principal : interface photographes, gestion des compétitions, upload et suivi des ventes.
- Dockerfile standard SPA avec Nginx.
- Dépendances : `axios`, `lucide-react`, `react-router-dom`, `zustand`, `react-hot-toast`.

### 5.2 `frontend-client`

- React 19, TypeScript 6, Vite 8, PWA.
- Cible mobile-first pour les athlètes.
- SSR léger pour les profils publics via FastAPI et template HTML.
- Dépendances additionnelles : `react-qr-code`, `vite-plugin-pwa`.

### 5.3 Qualité et tests

- Les deux frontends disposent de scripts `lint`, `build`, `test`, `preview`.
- DevDependencies incluent Playwright et Vitest.
- Présence de `package-lock.json` suggère npm lock, mais pas de pnpm ou yarn.

### 5.4 Observations

- Les versions des packages sont modernes mais potentiellement instables (`react@19`, TypeScript `~6.0.2`).
- Les Dockerfiles frontaux sont classiques et adaptés aux SPA.
- `frontend-client` bénéficie d’un usage PWA, ce qui est pertinent pour la cible athlète mobile.

## 6. CI/CD et déploiement

### 6.1 Jenkins

- Pipeline défini dans `Jenkinsfile`.
- Étapes clés : clone, lint, tests, build Docker, scan Trivy, déploiement, migration DB, E2E Playwright, scan OWASP ZAP.
- Le pipeline utilise des conteneurs Docker pour l’exécution des frontends.

### 6.2 Docker Compose

- `docker-compose.yml` orchestre tous les services nécessaires.
- Le backend utilise `env_file: ./backend/.env`.
- Les images frontend sont exposées sur les ports 5173 et 5174 via les services `frontend-web` et `frontend-client`.
- Les services `ai-api` et `ai-worker` partagent la même image `backend/worker_ai/Dockerfile`, ce qui peut être acceptable, mais mériterait une clarification fonctionnelle.

### 6.3 Observations CI/CD

- Le pipeline est complet mais potentiellement coûteux : `npm install` à chaque lint/test de frontend, `docker run` pour chaque job.
- Le déploiement copie `.env.example` en fallback si `.env` manquant, ce qui peut masquer un état de configuration incorrect.
- Le pipeline exécute un scan ZAP sur `http://localhost:8000`, utile mais doit être confié à une étape dédiée de test d’intrusion.

## 7. Documentation et gouvernance

- Dossier `docs/` présent et pertinent : configuration, run local, API reference, déploiement.
- Le README principal fournit une vision claire du monorepo.
- Une documentation supplémentaire serait utile pour :
  - les rôles et permissions métier,
  - la séparation des services IA/backends,
  - les exigences de sécurité pour les données biométriques,
  - le modèle d’architecture réseau Docker en production.

## 8. Observations générales

### 8.1 Points forts

- Architecture multi-service bien organisée.
- Utilisation d’un service IA séparé avec Qdrant pour la biométrie.
- Bon usage de FastAPI, rate limiting, et d’une approche asynchrone avec ARQ.
- Présence de tests backend et frontend, ainsi qu’une pipeline CI/CD détaillée.
- Forte orientation mobile-first sur le client athlète avec SSR pour SEO.

### 8.2 Risques et améliorations

- `SECRET_KEY` et les secrets webhook sont définis par défaut dans `.env.example` et doivent absolument être changés en production.
- Utiliser un secret en query param pour les callbacks internes n’est pas recommandé ; préférer un header HMAC ou une authentification interne.
- Disparité des versions Python entre `backend` (3.13) et `worker_ai` (3.11).
- Le service IA n’affiche pas d’authentification explicite ; le port est exposé publiquement dans Docker Compose.
- Le microservice worker a une dépendance OpenCV qui augmente la surface de maintenance et la taille d’image.
- L’usage d’une table JSON flexible (`settings`, `packs`) est pratique mais nécessite une gouvernance de schéma et des validations métier.
- Le dossier `zopic_photos_app/` semble être un projet Flutter séparé non intégré au reste de la stack.
- Les logs `hs_err_pid*` et `replay_pid*` présents à la racine ne sont pas liés au code source et devraient être nettoyés ou archivés ailleurs.

## 9. Recommandations prioritaires

1. Sécuriser les secrets en production : `SECRET_KEY`, `PAYMENT_WEBHOOK_SECRET`, `S3_*`, `QDRANT_URL`.
2. Remplacer le callback secret en query param par un header d’authentification interne ou une signature HMAC.
3. Aligner les versions Python backend / worker IA si possible.
4. Documenter clairement les flux de données biométriques et les obligations RGPD/consentement.
5. Ajouter un verrouillage de dépendances (`uv.lock`, `package-lock.json`) et vérifier qu’il est cohérent avec le pipeline.
6. Simplifier le pipeline Jenkins en capitalisant sur le cache npm et en évitant les installations répétées à chaque step.
7. Vérifier que `ai-api` et `ai-worker` ne sont pas exposés publiquement sans protection réseau.
8. Ajouter des tests E2E dédiés au parcours biométrique et au paiement sécurisé.

## 10. Conclusion

ZoPic Studio présente une base solide avec une architecture moderne et un fort potentiel fonctionnel. Le socle technique est bien bâti, mais plusieurs points de sécurité, de configuration et de gouvernance doivent être clarifiés avant une mise en production fiable.

Le projet est globalement bien structuré, mais il mérite une attention particulière sur la gestion des secrets, l’isolation des services IA et la documentation opérationnelle.
