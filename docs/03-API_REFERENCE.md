# Référence de l'API (FastAPI)

Toutes les routes de l'API ZoPic Studio sont préfixées par `/api/v1`.
La documentation interactive (Swagger UI) est générée automatiquement et disponible sur `/docs` (ex: `http://localhost:8000/docs`).

## Domaines Principaux

### Auth (`/api/v1/auth`)
- `POST /request-otp` : Demander un code SMS (limité à 3/min).
- `POST /verify` : Vérifier le code et obtenir un JWT.

### Athlètes (`/api/v1/athletes`)
- `GET /me/timeline` : Récupère la timeline sportive.
- `GET /me/gallery` / `POST /me/gallery` : Gérer la galerie d'images publiques.
- `GET /{slug}` : Récupère les données publiques d'un athlète (pour le frontend SSR).

### Compétitions & Epreuves (`/api/v1/competitions`)
- `POST /` : Créer une compétition (réservé aux photographes authentifiés).
- `POST /{id}/epreuves` : Ajouter des épreuves.

### Stockage (`/api/v1/storage`)
- `POST /upload-url` : Générer un lien S3 pour l'upload direct (contournant le serveur). Requis : Rôle photographe.
- `GET /download-url` : Récupérer une URL pré-signée S3. Requis : Authentification.

### Téléchargements (`/api/v1/orders/{order_id}/photos/{photo_id}/download`)
- `GET /` : Télécharger une photo achetée. Requis : Correspondance exacte entre `order.user_id` et l'utilisateur connecté, ou fourniture d'un en-tête `X-Session-ID` valide pour les commandes invitées.

### Reconnaissance Faciale (`/api/v1/faces`)
- `POST /search` : Rechercher des photos par selfie (Biométrie). Retourne des URLs filigranées et des prix.
- `POST /forget` : Supprimer les données biométriques.

### Paiements (`/api/v1/payments`)
- `POST /orders` : Initier un paiement via PayDunya.
- `POST /paydunya-webhook` : Gérer la confirmation de paiement (protégé par `PAYMENT_WEBHOOK_SECRET`).

---
> **Note** : Pour utiliser l'API, envoyez le header `Authorization: Bearer <votre_jwt>`. Pour les sessions invités, utilisez le header `X-Session-ID: <uuid>`.
