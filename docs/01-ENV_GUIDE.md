# Configuration des Variables d'Environnement (.env)

ZoPic Studio utilise des variables d'environnement pour gérer ses configurations, en particulier dans le dossier `backend/`. Copiez le fichier `.env.example` vers `.env` et ajustez les valeurs.

## Section par Section

### Base de données (PostgreSQL/SQLite)
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db # Local
# DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname # Prod
```

### Redis (ARQ / Event Bus)
```env
REDIS_URL=redis://localhost:6379/0
```

### Sécurité (JWT & Callbacks)
```env
SECRET_KEY=une_cle_secrete_longue_et_aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Cloudflare R2 / MinIO (Stockage)
```env
S3_ACCESS_KEY=r2_access_key
S3_SECRET_KEY=r2_secret_key
S3_REGION=auto
S3_BUCKET_NAME=zopic-storage
S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
```

### PayDunya (Paiements)
```env
PAYDUNYA_MASTER_KEY=...
PAYDUNYA_PRIVATE_KEY=...
PAYDUNYA_TOKEN=...
PAYDUNYA_MODE=test # test ou live
PAYMENT_SIMULATION_MODE=False # Doit être False en production
PAYMENT_WEBHOOK_SECRET="changez-ce-secret-en-prod" # Pour valider la signature (HMAC) des webhooks
```

### IA & Qdrant (Biométrie)
```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY= # Optionnel en local
FACE_MATCH_THRESHOLD=0.85 # Seuil de similarité pour la reconnaissance faciale (Cosine)
```

> [!CAUTION]
> Ne versionnez jamais votre fichier `.env`. Il est listé dans le `.gitignore`.

---

## Versions de Python (Divergence MVP)

> [!NOTE]
> Actuellement, le projet utilise deux versions de Python distinctes :
> - **Backend** : Python 3.13 (pour la rapidité, la compatibilité asyncio et les nouveautés de la syntaxe)
> - **Worker IA** : Python 3.11 (car InsightFace et certaines dépendances ONNX Runtime n'ont pas encore de *wheels* natives ou de compatibilité garantie avec 3.13)
>
> **Décision (Phase 1 / MVP)** : Cet écart est volontaire et documenté. Il permet de bénéficier des performances de 3.13 sur l'API principale tout en garantissant la stabilité du worker biométrique. L'uniformisation se fera en **Phase 2** lorsque l'écosystème IA aura rattrapé Python 3.13.
