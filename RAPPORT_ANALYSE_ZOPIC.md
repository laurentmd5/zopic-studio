# Rapport d'analyse exhaustive - ZoPic Studio

Date d'analyse : 2026-08-06  
Workspace : `E:\ZoPic Studio`  
Portée : monorepo complet, hors dépendances générées (`node_modules`, `.venv`)  
Résultat de vérification : tests unitaires backend et frontends exécutés avec succès

---

## 1. Synthèse exécutive

ZoPic Studio est un monorepo B2B2C orienté photo sportive, avec un backend FastAPI modulaire, deux applications web React/Vite, une application Flutter, un microservice IA Python, une base PostgreSQL, Redis/Arq, stockage S3 compatible MinIO/R2, Qdrant et un pipeline Docker/Jenkins.

Le produit implémenté correspond bien au coeur du MVP décrit dans `Dossier de Conception Produit.txt` : inscription OTP, gestion photographe, compétitions, albums/épreuves, upload par URL présignée, watermark, recherche faciale, achat, téléchargement, favoris, profils publics d'athlètes, galerie, timeline, archives ZIP et abonnements.

Le projet est déjà assez avancé techniquement : 127 tests backend passent, 14 tests frontend pro passent, 23 tests frontend client passent. La couverture fonctionnelle est large pour un MVP. En revanche, plusieurs points bloquent une mise en production sereine : incohérence de préfixes API, sécurité permissive, OTP non durci, webhook paiement non vérifié, CORS ouvert, endpoints de simulation exposés, secrets et valeurs locales trop présents, documentation README encore générique, et beaucoup de texte source encodé de manière cassée.

Verdict : base solide de MVP, mais phase de stabilisation indispensable avant beta publique.

---

## 2. Cartographie du dépôt

### 2.1 Racine

| Chemin | Rôle |
|---|---|
| `backend/` | API principale FastAPI, modèles SQLAlchemy, tests pytest, workers image |
| `backend/worker_ai/` | API et worker IA séparés pour InsightFace, Qdrant et archives ZIP |
| `frontend-web/` | Interface web photographe/pro, React + Vite |
| `frontend-client/` | PWA client/sportif, React + Vite + PWA |
| `zopic_photos_app/` | Application Flutter mobile, état plus léger/prototype |
| `tests-e2e/` | Suite Playwright transverse avec mocks |
| `docker-compose.yml` | Orchestration locale/prod Docker Compose |
| `Jenkinsfile` | Pipeline CI/CD complet |
| `Dossier de Conception Produit.txt` | Document produit de référence |

### 2.2 Volumétrie applicative

Inventaire hors dépendances et lockfiles :

| Métrique | Valeur |
|---|---:|
| Fichiers projet analysables | 300 |
| Fichiers code applicatif `.py`, `.ts`, `.tsx`, `.dart` | 200 |
| Fichiers de test détectés | 58 |

Remarque : la racine contient plusieurs fichiers `hs_err_pid*.log` et `replay_pid*.log`. Ils ressemblent à des crash dumps Java/JVM générés localement et devraient être supprimés du dépôt puis ignorés.

---

## 3. Stack technique

### 3.1 Backend principal

| Couche | Technologie |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy async |
| Validation | Pydantic v2 |
| DB | PostgreSQL en cible, SQLite mémoire en tests |
| Migrations | Alembic |
| Jobs | Arq + Redis |
| Images | Pillow |
| Stockage objet | S3 compatible via `aioboto3` |
| Paiement | PayDunya, simulation possible |
| Auth | OTP SMS + JWT |
| Tests | pytest, pytest-asyncio, httpx ASGITransport |

### 3.2 IA

| Couche | Technologie |
|---|---|
| Détection visage | InsightFace `buffalo_l` |
| Runtime | ONNX Runtime CPU |
| Traitement image | OpenCV headless |
| Base vectorielle | Qdrant |
| Queue | Arq, queue `arq:ai_queue` |

### 3.3 Frontends

| Application | Stack | Port dev |
|---|---|---:|
| `frontend-web` | React 19, TypeScript, Vite, Zustand, axios, lucide-react | 5173 |
| `frontend-client` | React 19, TypeScript, Vite, Zustand, axios, vite-plugin-pwa | 5174 |
| `zopic_photos_app` | Flutter, Riverpod, go_router, Dio | web/mobile |

### 3.4 Infrastructure

Docker Compose démarre :

| Service | Image | Port exposé |
|---|---|---:|
| PostgreSQL | `postgres:16-alpine` | 5433 -> 5432 |
| Redis | `redis:7-alpine` | 6380 -> 6379 |
| MinIO | `minio/minio` | 9002/9003 |
| Qdrant | `qdrant/qdrant` | 6335/6336 |
| Backend | `zopic-studio-backend` | 8000 |
| AI API | `zopic-ai-api` | 8001 |
| AI Worker | `zopic-ai-worker` | queue |
| Frontend pro | `zopic-frontend-web` | 5173 |
| Frontend client | `zopic-frontend-client` | 5174 |

---

## 4. Architecture globale

Le backend est un monolithe modulaire. Chaque domaine possède généralement :

- `models.py` pour SQLAlchemy
- `schemas.py` pour Pydantic
- `router.py` pour FastAPI
- `service.py` pour la logique métier
- parfois `handlers.py` pour les événements métier

Modules backend identifiés :

| Module | Responsabilité |
|---|---|
| `auth` | OTP, JWT, utilisateur, profil photographe |
| `competitions` | Compétitions, épreuves/albums, photos, packs |
| `storage` | URLs présignées upload/download |
| `face_recognition` | Proxy vers le service IA |
| `payments` | Commandes, PayDunya, webhooks, achats |
| `downloads` | Permissions, tokens, logs de téléchargement |
| `archives` | Génération ZIP asynchrone et SSE |
| `favorites` | Favoris invités ou connectés |
| `athletes` | Profil athlète, timeline, galerie, partages |
| `public` | API publique de profil athlète |
| `subscriptions` | Plans, abonnements, stockage |
| `audit` | Modèle d'audit, encore peu exploité |

Cette structure est saine pour un MVP : elle garde un déploiement simple tout en préparant une extraction future de l'IA, du stockage ou du paiement.

---

## 5. Backend principal

### 5.1 Entrée FastAPI

Fichier : `backend/app/main.py`

Constats :

- L'application expose `/health`.
- Les templates Jinja2 servent le rendu SSR minimal des profils publics `"/@{slug}"`.
- Les routers principaux sont inclus depuis `app.modules.*`.
- Les handlers downloads et athletes sont importés pour enregistrer les abonnements à l'event bus.
- CORS est configuré avec `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.

Risque important : `allow_origins=["*"]` combiné à `allow_credentials=True` est trop permissif et problématique pour une application avec JWT, paiement et données personnelles.

### 5.2 Configuration

Fichier : `backend/app/core/config.py`

Variables obligatoires :

- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET_NAME`
- `QDRANT_URL`
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`
- `EMAILS_FROM_EMAIL`, `EMAILS_FROM_NAME`

Variables avec défaut :

- `ACCESS_TOKEN_EXPIRE_MINUTES=15`
- `REFRESH_TOKEN_EXPIRE_DAYS=7`
- `S3_REGION=us-east-1`
- `PAYMENT_SIMULATION_MODE=True`
- `PAYMENT_WEBHOOK_SECRET="test_webhook_secret"`

Points à corriger :

- `PAYMENT_SIMULATION_MODE=True` par défaut est dangereux.
- `PAYMENT_WEBHOOK_SECRET` a une valeur de test par défaut.
- Il faut un `.env.example` maintenu et validé par CI.
- Les frontends utilisent `localhost` en dur au lieu d'une variable d'environnement.

### 5.3 Authentification

Fichiers :

- `backend/app/modules/auth/router.py`
- `backend/app/modules/auth/service.py`
- `backend/app/core/security.py`

Fonctionnement :

1. `POST /auth/request-otp` génère un OTP à 6 chiffres.
2. Le code est stocké en base avec expiration 10 minutes.
3. `POST /auth/verify` valide le code, marque l'OTP utilisé, crée l'utilisateur si nécessaire et renvoie un JWT.
4. `GET /auth/me` renvoie l'utilisateur courant.
5. `PUT /auth/me/profile` crée/met à jour le profil photographe et active `is_photographer`.

Forces :

- Flux passwordless adapté au marché mobile.
- Expiration OTP présente.
- OTP marqué comme utilisé.

Risques :

- Génération OTP avec `random.randint`, non cryptographique.
- Pas de rate limiting par téléphone/IP.
- Pas de limitation du nombre d'essais.
- Pas de refresh token implémenté malgré la config.
- Incohérence frontend : `frontend-web/src/services/authService.ts` envoie `application/x-www-form-urlencoded` avec `username/password`, alors que le backend attend un JSON `OTPVerify`.
- Le token OAuth2 indique `tokenUrl="api/v1/auth/verify"`, mais les routes backend ne sont pas toutes sous `/api/v1`.

### 5.4 Compétitions, albums et photos

Fichiers :

- `backend/app/modules/competitions/router.py`
- `backend/app/modules/competitions/service.py`
- `backend/app/modules/competitions/models.py`

Entités :

- `Competition`
- `Epreuve`
- `Photo`
- `Favorite`

Fonctionnement :

- Un photographe authentifié crée une compétition.
- Les compétitions publiques sont listées.
- Les compétitions privées exigent un `access_code`.
- Les épreuves structurent les albums.
- L'ajout photo crée la ligne DB, calcule une clé watermark, puis déclenche deux jobs Arq :
  - `generate_watermark`
  - `extract_faces` sur queue `arq:ai_queue`

Forces :

- Séparation métier claire.
- Packs de prix stockés en JSON.
- Processing asynchrone déjà branché.

Risques :

- Création d'épreuve et ajout de photo ne vérifient pas l'identité du photographe propriétaire.
- Le calcul `watermark_key = s3_object_key.replace("originals/", "watermarks/")` dépend fortement de la convention de chemin.
- Les statuts de compétition du dossier produit ne sont pas réellement modélisés.
- `settings` et `packs` en JSON donnent de la flexibilité, mais nécessitent validation stricte côté schéma.

### 5.5 Stockage

Fichiers :

- `backend/app/modules/storage/router.py`
- `backend/app/modules/storage/service.py`
- `backend/app/infrastructure/s3_client.py`

Fonctionnement :

- Génération d'URL présignée pour upload.
- Génération d'URL présignée pour download.
- Le client upload directement vers S3/MinIO.

Forces :

- Architecture scalable pour upload photo.
- Évite de faire transiter les gros fichiers par l'API.

Risques :

- Validation type/taille fichier à renforcer.
- Pas de scan antivirus ou validation image profonde.
- Quotas abonnement/stockage pas encore reliés à l'upload.
- Pas de stratégie de suppression des objets orphelins visible dans le code.

### 5.6 Paiements

Fichiers :

- `backend/app/modules/payments/router.py`
- `backend/app/modules/payments/service.py`
- `backend/app/modules/payments/models.py`
- `backend/app/modules/payments/paydunya_client.py`

Fonctionnement :

- Création de commande à partir d'une liste de `photo_ids`.
- Recalcul serveur du montant attendu.
- Support achat invité via `X-Session-ID`.
- Création facture PayDunya.
- Webhook PayDunya met la commande en `PAID`.
- Création ledger `PhotoSale` avec split 75% photographe / 25% plateforme.
- Publication d'un `PaymentCompletedEvent`.

Forces :

- Le montant est recalculé serveur.
- Ledger séparé des commandes.
- Idempotence partielle : une commande non pending n'est pas retraitée.

Risques critiques :

- Le webhook PayDunya n'est pas authentifié ni signé.
- `POST /payments/simulate-webhook` est exposé dans le router principal.
- `PAYMENT_SIMULATION_MODE=True` par défaut.
- `Order.status` est une colonne `String` malgré un enum Python.
- `OrderItem.price` est déclaré `Integer`, mais le calcul de pack utilise `avg_price = comp_total / photo_count`, donc un float peut être injecté.
- Les webhooks devraient être idempotents via clé transactionnelle robuste, pas seulement via statut.

### 5.7 Téléchargements et archives

Fichiers :

- `backend/app/modules/downloads/router.py`
- `backend/app/modules/downloads/models.py`
- `backend/app/modules/archives/router.py`
- `backend/app/modules/archives/models.py`
- `backend/worker_ai/app/worker.py`

Fonctionnement :

- Après paiement, les handlers créent des permissions de téléchargement.
- Téléchargement individuel : vérification commande, permission, expiration, génération token et URL présignée courte.
- Archives ZIP : création d'un enregistrement archive, job `generate_zip`, callback interne, stream SSE.

Forces :

- Traçabilité par `DownloadLog`.
- Permissions avec expiration.
- ZIP asynchrone avec retour de statut.
- SSE pour UX de progression.

Risques :

- Vérification d'accès téléchargement trop faible pour utilisateurs connectés : commentaire "en prod, vérifier current_user".
- `print` de debug dans route de téléchargement.
- Callback archive interne non authentifié.
- `EventSourceResponse` est importé depuis `fastapi.responses`, ce qui peut être fragile selon version Starlette/FastAPI.
- La construction `s3_keys = [f"originals/{p.s3_object_key.split('/')[-1]}"]` peut casser si la clé originale n'est pas exactement dans cette convention.

### 5.8 Profils athlètes et public

Fichiers :

- `backend/app/modules/athletes/router.py`
- `backend/app/modules/athletes/services.py`
- `backend/app/modules/athletes/models.py`
- `backend/app/modules/public/router.py`
- `backend/app/templates/public_profile.html`

Fonctionnement :

- Création et édition de profil athlète.
- Suggestions de slug.
- Galerie personnelle.
- Liens partagés.
- Timeline alimentée par achats.
- Profil public via `/api/v1/public/athletes/{slug}`.
- Route SSR `/@{slug}` pour métadonnées Open Graph.

Forces :

- Bonne base pour le positionnement "ZoPic Athlete".
- Séparation API publique / page SSR.
- Gestion de visibilité `PUBLIC`, `LINK_ONLY`, `PRIVATE`.

Risques :

- Les niveaux `LINK_ONLY` nécessitent une politique exacte : indexable ou non, visible API ou non.
- Protection contre énumération de slugs à renforcer.
- Les statistiques sont mises à jour via event bus in-memory, donc non durable si le process meurt.

### 5.9 Event bus interne

Fichier : `backend/app/core/events.py`

Implémentation in-memory avec `asyncio.create_task`.

Forces :

- Simple et utile pour découpler paiement, downloads, stats.

Risques :

- Aucun retry durable.
- Perte d'événements en cas de crash process.
- Échecs seulement loggés.
- Ne convient pas aux actions critiques post-paiement sans mécanisme de rattrapage.

---

## 6. Microservice IA

### 6.1 API IA

Fichier : `backend/worker_ai/app/main.py`

Endpoints :

- `GET /health`
- `POST /search`

Fonctionnement :

1. Reçoit un selfie.
2. Extrait les embeddings via InsightFace.
3. Prend le premier visage.
4. Recherche dans Qdrant collection `faces`.
5. Renvoie les 20 meilleurs résultats avec seuil `0.6`.

Risques :

- Catch global `Exception` transformé en 500, même pour des cas métier.
- Seuil `0.6` plus bas que le dossier produit qui mentionne `0.85`.
- Collection unique `faces`, alors que le dossier produit recommande une isolation par événement.
- Pas de consentement/liveness côté API.
- Pas de limite taille fichier ni validation MIME approfondie.

### 6.2 Worker IA

Fichier : `backend/worker_ai/app/worker.py`

Jobs :

- `extract_faces`
- `generate_zip`

Forces :

- Queue séparée `arq:ai_queue`.
- Upsert Qdrant avec payload riche.
- Génération ZIP asynchrone.

Risques :

- Logs via `print`.
- Identifiants MinIO par défaut dans le code.
- Pas de retry/backoff explicite visible.
- Pas de suppression/TTL des vecteurs faciaux.
- Pas de versionnement modèle dans les payloads Qdrant.

---

## 7. Frontend web photographe/pro

Chemin : `frontend-web/`

### 7.1 Routes

Fichier : `frontend-web/src/App.tsx`

Routes :

- `/login`
- `/`
- `/competitions`
- `/competitions/:competitionId`
- `/settings`
- `/billing`
- `/payouts`

### 7.2 Services API

Fichiers :

- `src/services/api.ts`
- `src/services/authService.ts`
- `src/services/competitionsService.ts`

Constats :

- Base URL codée en dur : `http://localhost:8000/api/v1`.
- Intercepteur ajoute `Authorization: Bearer`.
- 401 force logout et redirect `/login`.
- Services pour compétition, épreuves, photos, packs, upload.

Risques :

- Les routes backend `auth`, `competitions`, `storage`, `payments`, `subscriptions`, `downloads`, `archives`, `faces` ne sont pas toutes préfixées `/api/v1`; le frontend risque d'appeler des URLs inexistantes.
- `authService.verifyOtp` utilise form-data OAuth2, mais backend attend JSON.
- Pas de guard explicite visible dans `App.tsx`; la protection semble dépendre du layout/store.
- Les README restent ceux du template Vite.

### 7.3 État local

Zustand est utilisé pour auth et thème. Les tests couvrent les stores et services principaux.

---

## 8. Frontend client / PWA sportif

Chemin : `frontend-client/`

### 8.1 Routes

Fichier : `frontend-client/src/App.tsx`

Routes principales :

- `/`
- `/auth`
- `/search`
- `/competition/:id`
- `/competition/:id/search`
- `/checkout`
- `/payment`
- `/purchases`
- `/dashboard`
- `/timeline`
- `/identity/activate`
- `/profile/edit`
- `/profile/gallery`
- `/profile/shares`
- `/@:handle`

L'application a une logique mobile-first avec conteneur téléphone, sauf pour les profils publics.

### 8.2 PWA

Fichier : `frontend-client/vite.config.ts`

Fonctionnalités :

- `vite-plugin-pwa`
- Manifest `ZoPic Photos`
- Cache documents en `NetworkFirst`
- Cache JS/CSS en `CacheFirst`
- Cache images/fonts en `CacheFirst`
- Pas de cache API explicite

Risques :

- `includeAssets` référence `favicon.ico`, `apple-touch-icon.png`, `masked-icon.svg`, alors que les assets présents semblent plutôt `favicon.svg`, `hero_athlete.jpg`, `icons.svg`.
- Icônes PWA `pwa-192x192.png` et `pwa-512x512.png` non visibles dans l'inventaire.
- Couleur PWA très orientée marron, cohérente avec le dossier produit mais à vérifier contre les derniers CSS.

### 8.3 Auth client

Fichier : `frontend-client/src/store/authStore.ts`

Le token est stocké sous clé `guest-token`, même pour un JWT utilisateur. Cela peut créer de la confusion entre session invitée et session authentifiée.

### 8.4 API identité

Fichier : `frontend-client/src/api/identity.ts`

Base URL également codée en dur : `http://localhost:8000/api/v1`.

---

## 9. Application Flutter

Chemin : `zopic_photos_app/`

Stack :

- Flutter SDK `^3.11.5`
- Riverpod
- go_router
- Dio
- Google Fonts
- cached_network_image
- flutter_staggered_grid_view
- lucide_icons

Structure observée :

- `lib/main.dart`
- `lib/core/router.dart`
- `lib/core/theme.dart`
- `features/home`
- `features/competition`
- `features/cart`
- `features/downloads`

État :

- Semble être une base mobile/prototype.
- Couverture beaucoup plus faible que les webapps.
- Le `README.md` est encore le README Flutter/Vite générique.

Recommandation :

- Décider si Flutter reste une cible active du MVP ou devient un backlog.
- Si cible active : aligner modèles, endpoints et flows avec `frontend-client`.

---

## 10. Tests et qualité

### 10.1 Tests exécutés

Commandes exécutées :

```powershell
npm.cmd test
```

dans `frontend-web` :

- 5 fichiers de test passés
- 14 tests passés
- Note : message jsdom `Not implemented: navigation to another Document`

dans `frontend-client` :

- 9 fichiers de test passés
- 23 tests passés

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

dans `backend` :

- 127 tests collectés
- 127 tests passés
- 9 warnings

### 10.2 Warnings backend

Warnings notables :

- Dépréciation Pydantic v2 : `class Config` à remplacer par `ConfigDict`.
- Starlette/FastAPI : usage `httpx` avec `starlette.testclient` déprécié.
- Qdrant client : impossible d'obtenir la version serveur dans un test.
- `RuntimeWarning` sur des `AsyncMock` non awaited dans certains tests compétition.
- Pytest n'a pas pu écrire dans `.pytest_cache` à cause d'un accès refusé local.

### 10.3 E2E

`tests-e2e/` contient des specs Playwright pour :

- PWA : checkout, discovery, favorites, identity, purchases, timeline
- Web pro : auth, competitions, dashboard
- Mock backend transverse

Les E2E n'ont pas été lancés dans cette analyse. La configuration attend des builds preview sur 5173 et 5174.

Risque : les mocks E2E utilisent des endpoints anciens ou divergents, par exemple `/auth/otp/send`, `/auth/otp/verify`, `/payments/init`, alors que le backend actuel expose plutôt `/auth/request-otp`, `/auth/verify`, `/payments/orders`.

---

## 11. API : problème majeur de préfixes

Le backend définit `API_V1_STR = "/api/v1"` et OpenAPI à `/api/v1/openapi.json`, mais les routers ne sont pas inclus de manière homogène.

Exemples :

| Router | Préfixe router | Inclusion dans `main.py` | URL réelle probable |
|---|---|---|---|
| auth | `/auth` | sans `/api/v1` | `/auth/...` |
| competitions | `/competitions` | sans `/api/v1` | `/competitions/...` |
| storage | `/storage` | sans `/api/v1` | `/storage/...` |
| payments | `/payments` | sans `/api/v1` | `/payments/...` |
| favorites | `/api/v1/favorites` | sans préfixe additionnel | `/api/v1/favorites/...` |
| athletes | aucun | inclus avec `/api/v1/athletes` | `/api/v1/athletes/...` |
| public | aucun | inclus avec `/api/v1/public` | `/api/v1/public/...` |

Les frontends appellent principalement `http://localhost:8000/api/v1/...`. Cela signifie que plusieurs appels critiques peuvent échouer en intégration réelle même si les tests unitaires passent.

Priorité : très haute.

Recommandation :

- Inclure tous les routers via `app.include_router(router, prefix=settings.API_V1_STR)` ou appliquer une convention unique.
- Éviter les préfixes `/api/v1` directement dans les routers.
- Mettre à jour frontends, tests unitaires et E2E en une fois.

---

## 12. Sécurité

### 12.1 Points positifs

- Authentification JWT.
- OTP expirant.
- Photos originales servies via URLs présignées.
- Paiements recalculés côté serveur.
- Permissions de téléchargement avec expiration.
- Données sensibles externalisées via variables d'environnement dans le backend principal.

### 12.2 Risques critiques

| Risque | Impact | Priorité |
|---|---|---|
| CORS ouvert avec credentials | Vol de données / appels cross-origin non maîtrisés | Critique |
| Webhook PayDunya non vérifié | Commandes frauduleusement marquées payées | Critique |
| Endpoint `simulate-webhook` exposé | Paiement simulable si accessible | Critique |
| OTP sans rate limit | Bruteforce / coût SMS | Critique |
| Routes création épreuve/photo sans owner check | Altération de données d'autres photographes | Haute |
| Callback archive non authentifié | Falsification état archive | Haute |
| Event bus in-memory pour actions post-paiement | Perte de permissions/stats si crash | Haute |
| API IA sans limite fichier | Risque DoS mémoire/CPU | Haute |

### 12.3 Données biométriques

Le dossier produit décrit consentement explicite, suppression immédiate des selfies, collections Qdrant éphémères et isolation par événement. Le code actuel :

- Ne stocke pas le selfie dans l'API IA, bon point.
- Stocke les embeddings dans une collection Qdrant unique `faces`.
- Ne montre pas de TTL ou nettoyage automatique des vecteurs.
- Ne montre pas d'audit dédié aux accès biométriques.
- Ne versionne pas le modèle IA dans les points Qdrant.

Écart important avant conformité CDP/RGPD-like.

---

## 13. Données et modèle relationnel

Tables principales observées :

| Domaine | Tables |
|---|---|
| Auth | `users`, `photographer_profiles`, `otp_codes` |
| Compétitions | `competitions`, `epreuves`, `photos`, `favorites` |
| Paiements | `orders`, `order_items`, `photo_sales`, `payouts` |
| Downloads | `download_permissions`, `download_tokens`, `download_logs` |
| Archives | `archives` |
| Athlètes | `athlete_profiles`, `athlete_statistics`, `athlete_gallery`, `athlete_shares` |
| Abonnements | `plans`, `subscriptions`, `storage_usage` |
| Audit | `audit_logs` |

Points forts :

- Modèle clair et aligné MVP.
- Ledger `photo_sales`.
- Distinction invité/connecté via `session_id` et `user_id`.
- Statistiques athlète séparées.

Points à renforcer :

- Contraintes uniques favorites `(user_id, photo_id)` et `(session_id, photo_id)`.
- Types enum DB cohérents.
- Index sur clés fréquentes : `paydunya_token`, `session_id`, `slug`, `photo_id`, `order_id`.
- Migration Alembic probablement incomplète face au nombre de modèles actuels : une seule version visible.
- Éviter `default={}` sur colonnes JSON mutables ; préférer callable.

---

## 14. CI/CD et déploiement

### 14.1 Jenkinsfile racine

Pipeline :

1. Clone
2. Tests backend avec `uv`
3. Tests frontend web via Docker Node
4. Tests frontend client via Docker Node
5. Build Docker images backend, IA, frontends
6. Préparation déploiement
7. Redémarrage Docker Compose
8. Migration DB et init Qdrant
9. Nettoyage images Docker

Forces :

- Pipeline complet.
- Tests avant build.
- Images taguées par build number.
- Déploiement Compose simple.

Risques :

- Installation `uv` dans Jenkins via `curl | sh`.
- Copie de `.env.example` si `.env` absent, mais `.env.example` n'est pas visible dans l'inventaire.
- Pas d'étape lint malgré scripts `lint`.
- Pas de scan sécurité dépendances/images.
- Pas d'étape E2E Playwright.
- Pas de rollback automatisé.

### 14.2 Docker

Backend Python 3.13, worker IA Python 3.11. C'est logique pour InsightFace, mais il faut surveiller les divergences.

Risque : `docker-compose.yml` utilise des identifiants MinIO par défaut (`minioadmin/minioadmin`) et expose plusieurs services directement sur l'hôte.

---

## 15. Écarts avec le dossier produit

| Sujet | Dossier produit | Code actuel | Écart |
|---|---|---|---|
| API base URL | `/api/v1` partout | préfixes mixtes | Fort |
| Refresh token | 7 jours, rotation | config seulement | Fort |
| Webhook paiement | signature/idempotence/reconciliation | webhook simplifié | Fort |
| Reconnaissance faciale | seuil 0.85, isolation événement | seuil 0.6, collection unique | Fort |
| Consentement biométrique | explicite | non visible API | Fort |
| Stockage quotas | plans et blocage | modèle présent, peu relié upload | Moyen |
| RAW -> JPEG | prévu | non visible | Moyen |
| Watermark invisible | prévu phase 2 | non présent | Normal |
| Galeries privées proofing | prévu | partiel/athlete gallery | Moyen |
| Multilingue | phase future | non présent | Normal |
| Monitoring | Prometheus/Grafana/Loki | non présent | Moyen |

---

## 16. Dette technique

### 16.1 Encodage

De nombreux fichiers affichent du mojibake (`Ã©`, `ÃƒÂ©`, `â€™`, etc.). Cela touche :

- commentaires
- messages d'erreur
- texte UI
- dossier produit
- certains mocks E2E

Impact :

- UX non professionnelle si les chaînes sont affichées.
- Difficulté de maintenance.
- Tests qui valident potentiellement du texte cassé.

Priorité : haute pour les textes visibles.

### 16.2 Documentation

Les README de `frontend-web` et `frontend-client` sont encore ceux du template React/Vite. Le backend README est vide ou non informatif dans la sortie lue.

À produire :

- README racine
- README backend
- README frontend-web
- README frontend-client
- guide `.env`
- guide run local
- guide API
- guide déploiement

### 16.3 Outillage

Scripts présents :

- `refactor.py`, `fix_tests.py`, `check_imports.py`, `check_db.py`, `check_cov.py`
- plusieurs scripts de build UI côté frontend

Risque : scripts ponctuels non documentés, pouvant devenir du bruit ou de la dette.

---

## 17. État Git local

Des modifications locales non commitées existent au moment de l'analyse :

- `frontend-web/src/components/common/PhotoLightbox.module.css`
- `frontend-web/src/components/layout/DashboardLayout.module.css`
- `frontend-web/src/pages/Billing.module.css`
- `frontend-web/src/pages/CompetitionDetail.module.css`
- `frontend-web/src/pages/Competitions.module.css`
- `frontend-web/src/pages/Dashboard.module.css`
- `frontend-web/src/pages/Payouts.module.css`
- `frontend-web/src/pages/Settings.module.css`
- `frontend-web/src/styles/global.css`

Je n'ai pas modifié ces fichiers. Le rapport a été ajouté séparément.

---

## 18. Recommandations priorisées

### Priorité 0 - Bloquants production

1. Uniformiser tous les préfixes API sous `/api/v1`.
2. Corriger les clients frontend après l'uniformisation.
3. Remplacer l'OTP `random` par `secrets`, ajouter rate limit, limite d'essais et cooldown SMS.
4. Restreindre CORS aux domaines attendus.
5. Désactiver/supprimer `/payments/simulate-webhook` hors développement.
6. Vérifier cryptographiquement le webhook PayDunya.
7. Ajouter vérification propriétaire sur création épreuve, ajout photo, gestion packs.
8. Authentifier le callback interne archive.
9. Externaliser toutes les base URLs frontend via `.env`.

### Priorité 1 - Stabilisation MVP

1. Corriger l'encodage des textes visibles.
2. Ajouter migrations Alembic complètes pour tous les modèles.
3. Remplacer event bus in-memory pour actions critiques post-paiement par job durable ou outbox table.
4. Corriger le type `OrderItem.price` pour éviter float dans integer.
5. Ajouter validation stricte des packs et des settings compétition.
6. Ajouter limites upload : taille, MIME, dimensions, nombre de fichiers.
7. Relier upload aux quotas d'abonnement.
8. Lancer et corriger la suite Playwright.
9. Ajouter lint/typecheck dans CI.

### Priorité 2 - Sécurité et conformité biométrique

1. Isoler Qdrant par compétition ou ajouter filtre obligatoire par compétition.
2. Ajouter TTL/nettoyage des embeddings.
3. Versionner les modèles IA dans Qdrant.
4. Ajouter consentement explicite côté client/API.
5. Journaliser les recherches biométriques.
6. Ajouter endpoint de suppression des données faciales.
7. Définir politique `LINK_ONLY`.

### Priorité 3 - Produit et exploitation

1. Compléter README et guide de lancement local.
2. Ajouter observabilité : logs structurés, métriques, healthchecks profonds.
3. Ajouter reconciliation paiement périodique.
4. Ajouter dashboard opérationnel ventes/uploads/jobs.
5. Décider du statut de l'app Flutter dans la roadmap.
6. Nettoyer logs JVM et fichiers temporaires de la racine.

---

## 19. Plan d'action proposé sur 10 jours

### Jour 1-2 : intégration API

- Fix préfixes `/api/v1`.
- Mise à jour frontends et tests.
- Ajout variables `VITE_API_BASE_URL`.
- Run backend + frontends + E2E smoke.

### Jour 3-4 : sécurité paiement/auth

- Rate limit OTP.
- OTP via `secrets`.
- Webhook PayDunya signé.
- Suppression endpoint simulate en prod.
- CORS par environnement.

### Jour 5-6 : autorisations et données

- Owner checks compétitions/épreuves/photos.
- Callback archive protégé.
- Contraintes DB.
- Alembic complet.

### Jour 7-8 : biométrie et stockage

- Filtrage Qdrant par compétition.
- TTL/cleanup embeddings.
- Validation upload.
- Quotas stockage.

### Jour 9-10 : qualité livraison

- Corriger encodage UI.
- Lancer Playwright.
- Ajouter lint/typecheck CI.
- Nettoyer racine.
- Rédiger README et `.env.example`.

---

## 20. Conclusion

ZoPic Studio a une base technique sérieuse : architecture modulaire, séparation web pro/client, IA externalisée, stockage objet, queue asynchrone, tests unitaires nombreux et pipeline Docker/Jenkins. Le périmètre MVP est déjà bien représenté dans le code.

La priorité n'est pas de réécrire, mais de consolider : rendre les URLs cohérentes, fermer les portes de sécurité, fiabiliser les paiements, protéger les flux biométriques, nettoyer l'encodage et documenter l'exploitation. Après ces corrections, le projet peut devenir une beta robuste et crédible pour des tests terrain avec photographes et sportifs.
