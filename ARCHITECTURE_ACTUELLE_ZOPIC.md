# Architecture actuelle du projet ZoPic Studio

## 1. Vue d'ensemble

ZoPic Studio est un monorepo orienté SaaS pour la gestion et la vente de photos sportives. Le produit relie trois grands acteurs :
- les photographes, qui uploadent des photos de compétitions,
- les athlètes, qui recherchent leurs photos via un selfie,
- les clients, qui achètent et téléchargent des photos.

L'architecture actuelle combine :
- un backend principal en Python/FastAPI,
- un microservice IA dédié à la reconnaissance faciale,
- deux frontends React/Vite (web pour photographes et client PWA pour athlètes),
- un projet Flutter supplémentaire,
- une infrastructure Docker Compose avec PostgreSQL, Redis, MinIO, Qdrant.

---

## 2. Architecture fonctionnelle

### 2.1 Backend principal

Le backend principal est l'orchestrateur métier du système. Il expose une API REST sous le préfixe `/api/v1` et couvre plusieurs domaines fonctionnels :
- authentification et profils utilisateurs,
- compétitions et épreuves,
- stockage de photos et URLs présignées,
- recherche biométrique,
- paiements et abonnements,
- téléchargements et archives,
- athlètes, favoris et profils publics.

Le point d'entrée principal est :
- [backend/app/main.py](backend/app/main.py)

### 2.2 Service IA

Le service IA est un sous-système séparé chargé de :
- recevoir un selfie depuis le backend,
- extraire un embedding du visage,
- rechercher des visages similaires dans Qdrant,
- retourner les résultats correspondant aux photos détectées.

Le point d'entrée du service est :
- [backend/worker_ai/app/main.py](backend/worker_ai/app/main.py)

Ce service est conçu pour être appelé par le backend, mais il fonctionne aussi comme un service distinct avec ses propres endpoints.

---

## 3. Structure du dépôt

### 3.1 Racine

Fichiers clés à la racine :
- [README.md](README.md) : présentation générale du projet.
- [docker-compose.yml](docker-compose.yml) : orchestration des services tiers et applications.
- [Jenkinsfile](Jenkinsfile) : pipeline CI/CD.
- [docs/](docs) : documentation technique et opérationnelle.

### 3.2 Backend

Structure principale :
- [backend/app/main.py](backend/app/main.py) : application FastAPI principale.
- [backend/app/core](backend/app/core) : configuration, base de données, sécurité, limiter.
- [backend/app/modules](backend/app/modules) : modules métier découpés par domaine.
- [backend/app/worker.py](backend/app/worker.py) : worker ARQ pour les tâches asynchrones.
- [backend/app/infrastructure](backend/app/infrastructure) : intégrations externes (S3, Qdrant, etc.).
- [backend/worker_ai](backend/worker_ai) : microservice IA.

### 3.3 Frontends

- [frontend-web](frontend-web) : portail web destiné aux photographes.
- [frontend-client](frontend-client) : PWA mobile-first destinée aux athlètes.
- [zopic_photos_app](zopic_photos_app) : projet Flutter distinct.

---

## 4. Architecture technique détaillée

### 4.1 Couche API

Le backend utilise FastAPI avec les éléments suivants :
- une application principale regroupant tous les routers,
- un router global monté sous `/api/v1`,
- CORS configuré pour les origines du frontend,
- un endpoint `/health` pour la supervision,
- un rendu SSR pour les profils publics via Jinja2.

Le point central d’initialisation de l’API est [backend/app/main.py](backend/app/main.py).

### 4.2 Couche de données

Le backend s’appuie sur :
- SQLAlchemy pour l’ORM,
- Alembic pour la gestion des migrations,
- AsyncSession pour les opérations asynchrones,
- une base PostgreSQL en environnement standard.

Le point d’accès à la base est défini dans :
- [backend/app/core/database.py](backend/app/core/database.py)

### 4.3 Couche d’intégration externe

Le système fait appel à plusieurs services externes :
- PostgreSQL : stockage principal des données métier.
- Redis : bus de messages et tâches asynchrones.
- MinIO/S3 : stockage des images originales et filigranées.
- Qdrant : base vectorielle pour la recherche faciale.

Ces composants sont démarrés dans [docker-compose.yml](docker-compose.yml).

### 4.4 Traitement asynchrone

Le backend utilise ARQ via [backend/app/worker.py](backend/app/worker.py) pour traiter certaines opérations de fond, notamment :
- traitement d’événements métier,
- mise à jour de statistiques athlètes,
- nettoyage des collections biométriques archivées.

Cette approche permet de déléguer les tâches lourdes et de conserver une API réactive.

---

## 5. Modules métier principaux

### 5.1 Authentification

Le module d’authentification gère :
- demande d’OTP,
- vérification du code OTP,
- génération et validation des JWT,
- profil utilisateur et mise à jour du profil photographe.

### 5.2 Compétitions

Le module compétitions gère :
- les compétitions,
- les épreuves,
- les photos liées à une épreuve,
- les configurations de packs et de visibilité.

### 5.3 Stockage

Le module stockage fournit :
- des URLs présignées pour l’upload direct vers S3/MinIO,
- des URLs présignées pour le téléchargement.

### 5.4 Reconnaissance faciale

Le module face recognition agit comme proxy vers le worker IA. Il :
- reçoit le selfie,
- envoie la demande au service IA,
- enrichit les résultats avec des URLs de téléchargement,
- enregistre des traces d’audit.

### 5.5 Paiements et abonnements

Le backend intègre :
- la création de commandes et de paiements,
- la gestion de webhooks,
- la prise en charge de plans d’abonnement et de limites de stockage.

### 5.6 Téléchargements et archives

Le système gère les archives ZIP de commandes, avec :
- création d’une archive en tâche asynchrone,
- callback de statut,
- stream SSE pour notifier l’état de progression.

### 5.7 Athlètes et profils publics

Le module athlètes supporte :
- profils publics,
- galleries,
- partages,
- timeline et statistiques.

---

## 6. Architecture front-end

### 6.1 Frontend web

Le frontend web est dédié aux photographes. Il est conçu pour :
- gérer les compétitions,
- uploader des photos,
- consulter des statistiques,
- piloter l’expérience de vente et de gestion de contenu.

Il utilise React, Vite, TypeScript et des services HTTP vers l’API backend.

### 6.2 Frontend client

Le frontend client est une PWA mobile-first conçue pour :
- permettre aux athlètes de retrouver leurs photos,
- afficher un profil public,
- acheter et télécharger des photos,
- utiliser un parcours simplifié sur mobile.

### 6.3 Projet Flutter

Le projet Flutter est un sous-projet distinct, probablement destiné à une expérience mobile complémentaire ou à un prototype. Il est organisé autour de :
- un thème central,
- un système de routing,
- un modèle de features modulaires,
- des dépendances comme Riverpod, Go Router et Dio.

---

## 7. Déploiement et infrastructure

### 7.1 Conteneurs

Le projet utilise Docker Compose pour orchestrer :
- la base de données PostgreSQL,
- Redis,
- MinIO,
- Qdrant,
- le backend API,
- le service IA,
- les frontends web et client.

### 7.2 CI/CD

Le pipeline Jenkins défini dans [Jenkinsfile](Jenkinsfile) couvre :
- clone du dépôt,
- linting,
- tests unitaires,
- build des images Docker,
- scan de vulnérabilités,
- déploiement,
- tests E2E,
- nettoyage.

---

## 8. Forces de l’architecture actuelle

- séparation claire entre API, services IA et interfaces,
- découpage métier en modules cohérents,
- support asynchrone avec Redis/ARQ,
- intégration de services externes modernes (Qdrant, MinIO, PostgreSQL),
- présence d’une vraie logique de produit autour de la biométrie et de l’achat de photos.

---

## 9. Points de vigilance

- la sécurité des secrets doit rester un axe prioritaire,
- les intercommunications internes doivent être protégées de manière explicite,
- la qualité opérationnelle doit être renforcée avec des tests d’intégration et une surveillance plus robuste,
- la documentation d’architecture doit être maintenue à mesure que le produit évolue.

---

## 10. Conclusion

L’architecture actuelle de ZoPic Studio est cohérente, moderne et adaptée à un produit SaaS orienté IA et multimodal. Elle repose sur un découpage fonctionnel clair entre backend, service IA et frontends, avec une bonne base infrastructurelle grâce à Docker et CI/CD.

Le système est déjà suffisamment structuré pour évoluer, mais il doit continuer à être renforcé sur les axes de sécurité, de fiabilité et de gouvernance technique.
