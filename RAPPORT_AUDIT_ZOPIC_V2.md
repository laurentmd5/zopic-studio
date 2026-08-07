# Rapport d'audit exhaustif v2 - ZoPic Studio

Date d'audit : 2026-08-06  
Contexte : audit relancé après corrections appliquées dans le workspace  
Rapport précédent : `RAPPORT_ANALYSE_ZOPIC.md`  
Nouveau rapport : `RAPPORT_AUDIT_ZOPIC_V2.md`

---

## 1. Synthèse exécutive

Le projet a nettement progressé depuis le premier audit. Les corrections les plus visibles concernent :

- centralisation des routes sous `/api/v1` via un `api_router`;
- restriction CORS par configuration;
- ajout de SlowAPI pour limiter `request-otp`;
- ajout d'un refresh token avec rotation et blacklist;
- ajout de migrations Alembic;
- ajout de contraintes/index sur favoris et lignes de commande;
- ajout d'un event bus basé sur ARQ au lieu d'un simple in-memory;
- ajout du consentement biométrique côté API;
- isolation Qdrant par compétition (`faces_v1_{competition_id}`);
- seuil facial relevé à `0.85`;
- ajout de docs racine et docs d'exploitation;
- pipeline Jenkins enrichi avec lint, scan sécurité, E2E/DAST placeholders.

Les tests unitaires et builds passent :

| Zone | Résultat |
|---|---:|
| Backend pytest | 129 passed |
| Frontend web Vitest | 14 passed |
| Frontend client Vitest | 23 passed |
| Frontend web build | OK |
| Frontend client build/PWA | OK |

En revanche, le projet n'est pas encore prêt production. Les risques restants les plus importants sont :

1. `frontend-web` envoie encore l'OTP en form-data alors que le backend attend JSON.
2. OTP encore généré avec `random.randint`, sans limite d'essais sur `/auth/verify`.
3. Stockage upload/download encore non authentifié.
4. Téléchargement HD vérifie mal l'identité utilisateur/session.
5. Secrets de paiement et callback sont transmis en query string et ont des défauts de test.
6. Les E2E Playwright transverses échouent massivement côté PWA.
7. La documentation API et `.env` ne correspond pas encore au code réel.
8. Les actions post-paiement sont en queue ARQ, mais sans outbox/retry/idempotence métier robuste.

Verdict : amélioration réelle, mais il reste des blocages de sécurité, intégration et QA avant beta publique.

---

## 2. État du workspace

`git status` montre de nombreuses modifications locales et nouveaux fichiers. Les changements touchent principalement :

- backend core : `config.py`, `events.py`, `security.py`, `limiter.py`, `main.py`;
- auth : refresh token, blacklist, tests;
- compétitions : owner checks, quota stockage, statuts;
- paiements : webhook renommé/protégé, simulation conditionnelle;
- IA : consentement, audit, collections Qdrant par compétition;
- migrations Alembic;
- README et docs;
- Jenkinsfile;
- CSS frontend web;
- page Search PWA.

Fichiers supprimés :

- scripts de diagnostic ponctuels : `check_cov.py`, `check_db.py`, `check_imports.py`, `fix_tests.py`, etc.

Fichiers ajoutés :

- `README.md`
- `docs/01-ENV_GUIDE.md`
- `docs/02-RUN_LOCAL.md`
- `docs/03-API_REFERENCE.md`
- `docs/04-DEPLOYMENT.md`
- `backend/app/core/limiter.py`
- `backend/app/worker.py`
- `backend/scripts/cleanup_biometrics.py`
- migrations `0746690a54ca_*`, `30d1e3db530b_*`
- `backend/tests/test_product_gaps.py`

---

## 3. Résultats de vérification

### 3.1 Backend

Commande :

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

Résultat :

- 129 tests collectés
- 129 tests passés
- 8 warnings

Warnings notables :

- `PydanticDeprecatedSince20` dans `favorites.router` et `athletes.schemas`;
- `StarletteDeprecationWarning` autour de `fastapi.testclient`;
- warnings `AsyncMock` non awaited dans certains tests compétition;
- Qdrant compatibility warning;
- cache pytest non écrit à cause d'un accès local refusé.

### 3.2 Frontend web

Commandes :

```powershell
npm.cmd test
npm.cmd run build
```

Résultat :

- 5 fichiers Vitest passés;
- 14 tests passés;
- build production Vite OK.

Warning :

- jsdom : `Not implemented: navigation to another Document`.

### 3.3 Frontend client/PWA

Commandes :

```powershell
npm.cmd test
npm.cmd run build
```

Résultat :

- 9 fichiers Vitest passés;
- 23 tests passés;
- build production Vite/PWA OK;
- service worker généré.

### 3.4 E2E Playwright transverse

Commande :

```powershell
npx.cmd playwright test
```

Résultat :

- timeout global après 180 secondes;
- 12 tests lancés;
- au moins 9 échecs PWA avant expiration;
- les tests web-pro ont commencé mais la commande a expiré avant résumé complet.

Échecs observés :

- `.btn-primary` introuvable sur `/competition/999`;
- texte `Marathon E2E` introuvable;
- bouton `Retrouver mes photos` introuvable;
- `input[name="slug"]` introuvable;
- profil public `@moussa.dkr` non rendu comme attendu;
- achats/timeline non affichés selon attentes.

Interprétation : les E2E ne sont plus alignés avec l'UI et les mocks. Ce n'est pas simplement un test flaky; la suite transverse est actuellement non fiable pour valider la release.

---

## 4. Corrections validées depuis l'audit v1

### 4.1 Préfixes API

Le backend centralise maintenant les routers dans `api_router` et les inclut avec `settings.API_V1_STR`.

Preuves :

- `backend/app/main.py:69-83`

Impact : la grande incohérence `/api/v1` relevée au premier audit est largement corrigée côté backend.

Réserve : les docs et certains mocks E2E ne sont pas encore alignés.

### 4.2 CORS

CORS n'est plus ouvert avec `*` par défaut. Les origines viennent de `BACKEND_CORS_ORIGINS`, avec fallback local.

Preuves :

- `backend/app/main.py:32-40`
- `backend/app/core/config.py:6`

Réserve : le fallback local est acceptable en dev, mais il faut forcer une configuration explicite en prod.

### 4.3 Rate limit OTP

SlowAPI est ajouté et `/auth/request-otp` est limité à `3/minute`.

Preuves :

- `backend/app/core/limiter.py`
- `backend/app/modules/auth/router.py:11-16`

Réserve : seul l'envoi OTP est limité; `/auth/verify` ne semble pas limiter les essais.

### 4.4 Refresh token

Refresh token avec `jti`, blacklist et rotation.

Preuves :

- `backend/app/core/security.py`
- `backend/app/modules/auth/models.py:35-40`
- `backend/app/modules/auth/service.py:65-92`
- `backend/tests/test_product_gaps.py`

Réserve : l'endpoint reçoit `refresh_token` en paramètre simple, pas dans un body structuré, et `get_current_user` ne vérifie pas que le token est de type `access`.

### 4.5 Owner checks compétitions

Création d'épreuve et ajout de photo vérifient maintenant le photographe propriétaire.

Preuves :

- `backend/app/modules/competitions/router.py`

Impact : un risque haute priorité du premier audit est partiellement corrigé.

### 4.6 Quotas stockage

`add_photo` vérifie `StorageUsage`, abonnement actif et plan avant d'ajouter une photo.

Preuves :

- `backend/app/modules/competitions/service.py:56-82`
- `backend/tests/test_product_gaps.py`

Réserve : le quota est mis à jour lors de l'enregistrement DB, pas au moment de l'upload présigné. Des fichiers peuvent encore être uploadés dans S3 sans être comptabilisés si le client n'appelle pas ensuite l'endpoint photo.

### 4.7 Biométrie

Améliorations :

- consentement obligatoire;
- limite 10 MB côté proxy backend;
- audit log `face_search`;
- collection Qdrant par compétition;
- seuil `0.85`;
- endpoint `forget`;
- payload Qdrant avec `created_at` et `model_version`.

Preuves :

- `backend/app/modules/face_recognition/router.py:21-73`
- `backend/worker_ai/app/main.py:37-47`
- `backend/worker_ai/app/worker.py:60-72`

Réserve : l'endpoint `/faces/forget` n'impose pas de consentement/auth forte; il supprime par similarité dans une compétition donnée, ce qui peut supprimer des embeddings d'autres personnes si le seuil matche.

### 4.8 Event bus

L'event bus publie vers ARQ au lieu d'exécuter des handlers en mémoire.

Preuves :

- `backend/app/core/events.py:16-38`
- `backend/app/worker.py`

Impact : meilleure durabilité que `asyncio.create_task`.

Réserve : si `enqueue_job` échoue, l'erreur est loggée mais le paiement reste marqué `PAID`. Il manque une outbox transactionnelle ou un mécanisme de rattrapage.

### 4.9 Migrations

Nouvelles migrations :

- `30d1e3db530b_audit_fixes.py`
- `0746690a54ca_add_tokenblacklist.py`

Elles ajoutent :

- contraintes uniques favoris;
- index sur `order_items`;
- table `token_blacklist`.

Réserve : ces migrations ne couvrent pas toutes les évolutions de modèle possibles, par exemple `Competition.status` si elle n'était pas déjà dans une migration antérieure.

---

## 5. Risques critiques restants

### 5.1 Auth frontend web cassée fonctionnellement

`frontend-web/src/services/authService.ts` envoie :

- `URLSearchParams`
- `username`
- `password`
- `Content-Type: application/x-www-form-urlencoded`

Preuves :

- `frontend-web/src/services/authService.ts:12-18`

Mais le backend attend `OTPVerify` JSON :

- `phone_number`
- `code`

Impact : la connexion réelle du portail photographe peut échouer malgré les tests unitaires.

Action :

- envoyer `api.post('/auth/verify', { phone_number, code })`;
- mettre à jour les tests frontend.

### 5.2 OTP encore faible

Le backend utilise toujours :

- `import random`
- `random.randint(100000, 999999)`

Preuves :

- `backend/app/modules/auth/service.py:1`
- `backend/app/modules/auth/service.py:30`

Risques :

- génération non cryptographique;
- pas de verrouillage après N tentatives;
- pas de suppression/invalidation des anciens OTP pour le même numéro;
- `/auth/verify` non rate-limité.

Action :

- utiliser `secrets.randbelow`;
- hasher les OTP stockés;
- limiter `/verify`;
- ajouter compteur d'essais et verrouillage temporaire.

### 5.3 Stockage non authentifié

`/storage/upload-url` et `/storage/download-url` n'ont pas de dépendance auth.

Preuves :

- `backend/app/modules/storage/router.py:17-33`
- commentaire explicitement non corrigé : `backend/app/modules/storage/router.py:21`

Impact :

- n'importe qui peut obtenir une URL upload;
- n'importe qui peut demander une URL download si la clé est connue;
- quotas et droits d'achat peuvent être contournés.

Action :

- protéger upload par photographe authentifié;
- protéger download par permission achat ou rôle propriétaire;
- intégrer quota avant génération URL présignée.

### 5.4 Téléchargement HD encore insuffisamment autorisé

Le téléchargement vérifie seulement :

- existence commande;
- si `order.session_id` et `x_session_id` sont présents, alors comparaison;
- présence permission;
- appartenance photo à commande.

Preuves :

- `backend/app/modules/downloads/router.py:30-37`

Problème :

- si la commande appartient à un `user_id`, il n'y a pas de `current_user`;
- si `order.session_id` existe mais `x_session_id` est absent, la condition ne bloque pas;
- un attaquant connaissant `order_id` et `photo_id` peut potentiellement récupérer l'URL si permission existe.

Action :

- exiger `current_user` ou `X-Session-ID`;
- comparer `order.user_id == current_user.id` ou `order.session_id == x_session_id`;
- rejeter absence de session pour commande invitée.

### 5.5 Webhooks et secrets en query string

Paiement :

- `secret` est un paramètre simple de la route PayDunya;
- comparaison directe avec `settings.PAYMENT_WEBHOOK_SECRET`.

Preuves :

- `backend/app/modules/payments/router.py:29-40`

Archive :

- callback généré avec `?secret={settings.SECRET_KEY}`;
- secret comparé ensuite depuis query param.

Preuves :

- `backend/app/modules/archives/router.py`

Risques :

- secrets exposés dans logs HTTP, reverse proxy, traces, analytics;
- `SECRET_KEY` JWT réutilisée pour callbacks internes;
- pas de HMAC sur body.

Action :

- header `X-Zopic-Signature`;
- HMAC SHA-256 du body avec secret dédié;
- `secrets.compare_digest`;
- ne jamais mettre `SECRET_KEY` dans une URL.

### 5.6 Defaults de production dangereux

`config.py` garde :

- `PAYMENT_SIMULATION_MODE=True`
- `PAYMENT_WEBHOOK_SECRET="test_webhook_secret"`

Preuves :

- `backend/app/core/config.py:30-31`

`.env.example` garde également :

- `SECRET_KEY="supersecretkey-change-it-in-production"`
- `PAYMENT_SIMULATION_MODE=True`
- `PAYMENT_WEBHOOK_SECRET="test_webhook_secret"`

Impact : en déploiement pressé, la simulation et les secrets test peuvent partir en prod.

Action :

- valeurs sensibles sans défaut en prod;
- variable `ENVIRONMENT`;
- validation startup qui refuse ces valeurs hors dev.

### 5.7 E2E non fiables

Les E2E transverses échouent côté PWA. Cela retire une grande partie de la confiance de release.

Action :

- synchroniser mocks avec routes actuelles;
- mettre à jour sélecteurs UI;
- ajouter `data-testid`;
- séparer E2E mocked et E2E intégration backend.

---

## 6. Risques élevés

### 6.1 Documentation API divergente

`docs/03-API_REFERENCE.md` mentionne des routes qui ne correspondent pas au backend :

- `POST /verify-otp` au lieu de `/auth/verify`;
- `/storage/presigned-upload-url` au lieu de `/storage/upload-url`;
- `/paydunya/create-invoice` au lieu de `/payments/orders`;
- `/paydunya/webhook` au lieu de `/payments/paydunya-webhook`.

Preuves :

- `docs/03-API_REFERENCE.md:10`
- `docs/03-API_REFERENCE.md:22-27`

Action : générer la doc depuis OpenAPI ou corriger manuellement.

### 6.2 Guide `.env` divergent

`docs/01-ENV_GUIDE.md` documente `AWS_*`, alors que le code attend `S3_*`.

Preuves :

- docs : `docs/01-ENV_GUIDE.md:27-31`
- code : `backend/app/core/config.py:14-18`

Action : harmoniser docs, `.env.example`, Docker Compose et code.

### 6.3 Jenkins ne bloque pas certains contrôles

Le Jenkinsfile contient :

- frontend lint avec `|| true`;
- Trivy avec `|| true`;
- E2E placeholder;
- DAST placeholder.

Preuves :

- `Jenkinsfile:48`
- `Jenkinsfile:55`
- `Jenkinsfile:125`
- `Jenkinsfile:198`
- `Jenkinsfile:210`

Impact : le pipeline donne une impression de couverture, mais ne bloque pas encore sur plusieurs qualités critiques.

Action :

- rendre lint bloquant;
- décider seuil Trivy bloquant;
- remplacer placeholders E2E/DAST par commandes réelles ou les retirer du pipeline annoncé.

### 6.4 `ruff` appelé mais non déclaré

Le pipeline exécute `uv run ruff check .`, mais `backend/pyproject.toml` ne montre pas `ruff` dans les dépendances lues. Il y a `slowapi`, mais pas `ruff`.

Preuves :

- Jenkins : `Jenkinsfile:41`
- pyproject : seul `slowapi` détecté par recherche.

Impact : stage lint backend susceptible d'échouer selon l'environnement.

Action : ajouter `ruff` au groupe dev ou installer explicitement dans CI.

### 6.5 Calcul des packs et prix en float

`avg_price = comp_total / photo_count` produit un float, injecté dans `OrderItem.price` déclaré `Integer`.

Preuves :

- `backend/app/modules/payments/service.py:71-75`
- `backend/app/modules/payments/models.py`

Impact :

- arrondis implicites;
- erreurs DB selon dialecte;
- ledger financier potentiellement incohérent.

Action :

- prix entiers uniquement;
- répartir le reste explicitement;
- conserver total commande égal à somme des lignes.

### 6.6 Search PWA encore simulée

`frontend-client/src/pages/SearchPage.tsx` garde `simulateSearch`, des images Unsplash et ne semble pas appeler `/api/v1/faces/search`.

Impact : le consentement UI a été ajouté, mais le flux réel selfie -> IA n'est pas intégré dans cette page.

Action :

- remplacer simulation par capture/upload réel;
- envoyer `competition_id`, `consent`, `file`;
- gérer résultats API et erreurs IA.

---

## 7. Dette technique et qualité

### 7.1 Encodage toujours cassé

Le mojibake reste très présent :

- README;
- docs;
- commentaires backend;
- messages UI;
- fichiers tests E2E;
- SearchPage.

Exemples visibles :

- `propulsÃ©e`
- `AthlÃ¨tes`
- `RÃ©fÃ©rence`
- `CamÃ©ra`

Impact :

- texte utilisateur potentiellement cassé;
- documentation moins crédible;
- maintenance pénible.

Action :

- convertir fichiers en UTF-8 proprement;
- ajouter contrôle CI léger contre séquences `Ã`, `Â`, `â€™`, etc. sur textes visibles.

### 7.2 Logs `print`

`print` reste dans :

- `downloads.router`;
- `worker_ai/app/worker.py`;
- `cleanup_biometrics.py`;
- `image_tasks.py`.

Action :

- remplacer par logging structuré;
- éviter fuite de clés, IDs et secrets.

### 7.3 Event bus pas transactionnel

Le paiement est marqué `PAID`, le ledger est créé, puis `event_bus.publish` envoie les jobs. Si Redis échoue :

- paiement OK;
- permission de téléchargement non créée;
- stats non mises à jour;
- simple log d'erreur.

Action recommandée :

- table `outbox_events`;
- transaction DB unique avec paiement/ledger/outbox;
- worker outbox avec retry/idempotence.

### 7.4 Migrations possiblement incomplètes

Les migrations ajoutées sont utiles, mais il faut vérifier `alembic upgrade head` depuis une base vide et depuis une base v1.

Points à vérifier :

- `Competition.status`;
- types enum existants;
- colonnes/index non couverts;
- compatibilité PostgreSQL réelle.

---

## 8. Modules backend - état par domaine

| Module | État v2 | Risque principal |
|---|---|---|
| `auth` | Progression forte avec refresh/blacklist/limiter | OTP et verify encore faibles |
| `competitions` | Owner checks et quota ajoutés | quota après upload, settings/packs peu validés |
| `storage` | Inchangé fonctionnellement | endpoints non authentifiés |
| `payments` | webhook protégé minimalement | secret query string, simulation par défaut |
| `downloads` | permissions/logs présents | contrôle identité insuffisant |
| `archives` | callback secret ajouté | secret en URL + SECRET_KEY réutilisée |
| `face_recognition` | consent/audit/limit ajoutés | forget dangereux, pas auth, exceptions larges |
| `worker_ai` | collection par compétition, seuil 0.85 | logs print, defaults MinIO, pas de TTL automatique |
| `athletes` | inchangé majoritairement | stats incrémentales non idempotentes |
| `subscriptions` | utilisé par quota | raccord upload incomplet |

---

## 9. Frontends - état par application

### 9.1 Frontend web pro

Points positifs :

- tests et build passent;
- API base maintenant cohérente avec `/api/v1`;
- CSS en cours d'amélioration.

Risques :

- auth OTP toujours incompatible avec backend;
- base URL encore codée en dur `http://localhost:8000/api/v1`;
- pas de variable `VITE_API_BASE_URL`;
- tests unitaires n'attrapent pas le mauvais format de `/auth/verify`.

### 9.2 Frontend client/PWA

Points positifs :

- tests et build passent;
- consentement UI ajouté sur recherche selfie;
- PWA build OK.

Risques :

- recherche selfie encore simulée;
- E2E PWA échouent;
- API identity base URL codée en dur;
- certaines routes/profils publics ne correspondent plus aux scénarios E2E.

### 9.3 Flutter

Aucun changement significatif observé dans cette passe. L'app Flutter reste un socle/prototype à clarifier dans la roadmap.

---

## 10. Priorisation des corrections

### P0 - À corriger avant toute beta publique

1. Corriger `frontend-web/src/services/authService.ts` pour envoyer JSON à `/auth/verify`.
2. Protéger `/api/v1/storage/upload-url` et `/api/v1/storage/download-url`.
3. Corriger l'autorisation de `/orders/{order_id}/photos/{photo_id}/download`.
4. Remplacer OTP `random` par `secrets`, ajouter rate limit/lockout sur `/auth/verify`.
5. Supprimer les secrets en query string, utiliser HMAC header.
6. Mettre `PAYMENT_SIMULATION_MODE=False` par défaut hors dev et refuser les secrets test au startup.
7. Corriger E2E PWA ou les sortir explicitement du statut "gating".

### P1 - Stabilisation release

1. Harmoniser `docs/01-ENV_GUIDE.md`, `.env.example`, `config.py` et Docker Compose.
2. Corriger `docs/03-API_REFERENCE.md` avec les routes réelles.
3. Intégrer réellement `/faces/search` dans la PWA.
4. Corriger le calcul des packs pour garder des entiers financiers.
5. Ajouter `ruff` aux dépendances dev ou corriger Jenkins.
6. Rendre lint frontend bloquant.
7. Remplacer placeholders E2E/DAST Jenkins par commandes réelles ou retirer les stages.

### P2 - Durabilité et conformité

1. Ajouter outbox transactionnelle pour événements post-paiement.
2. Ajouter cleanup biométrique planifié, testé, et documenté.
3. Ajouter auth/ownership sur `/faces/forget`.
4. Ajouter tests PostgreSQL/migrations sur base réelle.
5. Corriger encodage UTF-8 dans docs/UI/messages.
6. Remplacer `print` par logging structuré.

---

## 11. Plan d'action recommandé

### Sprint court 1-2 jours

- Fix auth frontend JSON.
- Protéger storage endpoints.
- Corriger download authorization.
- Changer OTP vers `secrets`.
- Ajouter tests ciblés pour ces 4 points.

### Sprint 3-5 jours

- HMAC webhooks paiement et archive.
- Env validation au startup.
- Corriger docs API/env.
- Corriger prix packs entiers.
- Rendre CI lint réellement bloquant.

### Sprint 1 semaine

- Réparer E2E PWA avec `data-testid`.
- Brancher vraie recherche IA dans PWA.
- Ajouter outbox post-paiement.
- Nettoyage UTF-8.

---

## 12. Conclusion

Les corrections appliquées vont dans la bonne direction : le squelette backend est plus cohérent, l'API est mieux préfixée, la biométrie est mieux cadrée, les événements sont moins fragiles, et la documentation commence à exister. Les tests unitaires et builds donnent une base rassurante.

Mais les zones restantes sont précisément celles qui protègent l'argent, les photos HD, les données biométriques et la connexion réelle. La prochaine étape ne devrait pas être d'ajouter des fonctionnalités; elle devrait fermer ces ouvertures et réaligner frontends, docs, mocks et backend.

