# ZoPic Studio

ZoPic Studio est une plateforme de partage et de vente de photos de sport, propulsée par l'Intelligence Artificielle (reconnaissance faciale).
Elle connecte les **photographes professionnels** (qui uploadent les photos d'une compétition) et les **athlètes** (qui retrouvent instantanément leurs photos via un selfie).

## Architecture du Projet (Monorepo)

- **`backend/`** : API REST en Python (FastAPI), traitement d'images asynchrone (ARQ), et IA biométrique (Qdrant).
- **`frontend-web/`** : Portail Web "Pro" pour les photographes (Vite + React).
- **`frontend-client/`** : PWA "Mobile-First" pour les athlètes (Vite + React), avec SSR basique pour le SEO des profils publics.

## Documentation Détaillée

Consultez le dossier `/docs` pour approfondir la configuration et le déploiement :
- [Guide des variables d'environnement (.env)](docs/01-ENV_GUIDE.md)
- [Lancer le projet en local](docs/02-RUN_LOCAL.md)
- [Référence de l'API](docs/03-API_REFERENCE.md)
- [Déploiement et CI/CD](docs/04-DEPLOYMENT.md)

---
*Projet développé pour optimiser l'expérience photographique sur les événements sportifs.*
