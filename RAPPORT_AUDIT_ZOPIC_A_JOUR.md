# Rapport d'audit à jour — ZoPic Studio

## 1. Résumé exécutif

Le projet ZoPic Studio est un monorepo cohérent et fonctionnel, structuré autour d'une API backend Python/FastAPI, d'un service IA dédié à la biométrie, de deux frontends React/Vite (photographes et athlètes), ainsi qu'un projet Flutter séparé. La base architecturale est solide et montre une volonté claire de séparer les responsabilités métier, l'interface utilisateur et le traitement d'images.

L'audit montre que le projet est globalement bien pensé, avec une bonne séparation des modules backend et un socle CI/CD complet. Les principaux axes à améliorer concernent la sécurité des secrets, la protection des services IA, la robustesse des callbacks internes, ainsi que la consolidation de la qualité opérationnelle et de la documentation.

## 2. État général du projet

### 2.1 Architecture globale

Le dépôt contient actuellement :
- un backend FastAPI principal,
- un service worker IA dédié,
- un frontend web pour photographes,
- un frontend client PWA pour athlètes,
- un projet Flutter distinct,
- une documentation et un pipeline Jenkins.

Cette architecture est adaptée à un produit SaaS orienté photos sportives, avec recherche biométrique, ventes et partage de contenus.

### 2.2 Niveau de maturité

Le projet atteint un niveau de maturité intermédiaire à avancé :
- modules métier présents,
- API bien découpée,
- tests backend et frontend intégrés,
- CI/CD Jenkins configuré,
- containers Docker disponibles.

En revanche, plusieurs points doivent être durcis avant une mise en production robuste et durable.

## 3. Audit technique par domaine

### 3.1 Backend

#### Points forts
- API FastAPI bien organisée avec plusieurs modules métiers distincts : auth, competitions, storage, face recognition, payments, subscriptions, favorites, downloads, archives et athletes.
- L'architecture suit une logique claire : routes, services, modèles, et dépendances injectées via `Depends`.
- Le backend expose un endpoint de santé (`/health`) et un système SSR pour les profils athlètes publics.
- L’usage de SQLAlchemy 2.x et d’Alembic est adapté à une application évolutive.

#### Points à améliorer
- La gestion des secrets et de la configuration reste critique. Le backend s’appuie sur des variables d’environnement strictement nécessaires, mais l’environnement de production doit être verrouillé.
- La validation métier et les schémas JSON utilisés dans certaines entités sont assez flexibles, ce qui facilite l’évolution mais complique la robustesse à long terme.
- Certains callbacks et flux internes reposent encore sur des mécanismes simples qui gagneraient à être sécurisés davantage.

#### Observations spécifiques
- Le module d’authentification est robuste sur le plan structurel, avec rate limiting et logique OTP/JWT.
- Le module de stockage utilise des URLs présignées pour éviter l’upload direct par le serveur.
- Le module de reconnaissance faciale est bien découplé et utilise un service externe dédié, ce qui est une bonne pratique.

### 3.2 Service IA

#### Points forts
- Le service IA est isolé dans un sous-projet distinct, ce qui est préférable pour la maintenance et le déploiement.
- Il communique avec Qdrant et avec le backend via des endpoints dédiés.
- La logique de recherche et de suppression faciale est clairement séparée entre `/search` et `/forget`.

#### Risques
- Le worker IA n’applique pas de mécanisme d’authentification visible dans le code lu ; la protection doit être assurée au niveau réseau ou derrière un reverse proxy.
- Les seuils de similarité pour la recherche biométrique sont codés en dur, ce qui limite la configurabilité.
- La dépendance à OpenCV et InsightFace augmente la surface de maintenance et le temps de build.

### 3.3 Frontend web (photographes)

#### Points forts
- L’application web est bien conçue pour un usage SaaS de gestion de compétitions et d’upload.
- L’utilisation de React + Vite + TypeScript est cohérente avec l’objectif produit.
- L’architecture permet une logique de séparation entre UI, services et états.

#### Points à améliorer
- Le frontend web est fonctionnel, mais l’audit ne permet pas encore de conclure à une couverture complète de tests UI métier.
- La qualité des composants et de la cohérence visuelle devrait être renforcée si l’outil est destiné à un usage professionnel intensif.

### 3.4 Frontend client (athlètes)

#### Points forts
- L’application PWA mobile-first est adaptée à la cible athlète.
- L’intégration du SSR pour les profils publics est pertinente pour le SEO et le partage social.
- La présence de fonctionnalités comme QR code, galerie et profil publique suit bien l’objectif produit.

#### Points à améliorer
- Le front client mérite une vérification plus fine sur la robustesse de la navigation, le cache PWA, et le rendu en cas d’erreur réseau.
- La logique d’état et de persistance locale doit être revue pour éviter les incohérences de données.

### 3.5 Projet Flutter

#### Points forts
- Le projet Flutter est bien structuré au niveau des dossiers (`core`, `features`, `main.dart`).
- L’usage de Flutter Riverpod, Go Router et Dio est judicieux pour une application modulaire.
- Le thème a été personnalisé avec une identité visuelle claire et cohérente.

#### Observations
- Le projet semble être un effort distinct du reste du monorepo, probablement à des fins de déploiement mobile ou d’exploration technique.
- La dépendance à `google_fonts` et à des packages modernes est acceptable, mais il serait utile de confirmer qu’elle est bien intégrée dans le plan de livraison global.
- Le thème actuel est bien défini, mais il manque encore une structure plus complète de design system si l’objectif est un produit réellement prêt à l’échelle.

## 4. Sécurité

### 4.1 Points positifs
- Le backend utilise un rate limiter, des secrets environnements et une logique de validation de webhook.
- Les uploads sont gérés via des URLs présignées.
- Les routes sensibles sont séparées et l’architecture évite un stockage centralisé des fichiers sur le serveur.

### 4.2 Risques majeurs
- Les secrets de production doivent être strictement externalisés et non laissés dans le code ou les exemples par défaut.
- Le callback interne avec secret en paramètre d’URL est moins sûr qu’un mécanisme basé sur un header ou une signature HMAC.
- Les endpoints IA doivent être protégés de façon explicite au niveau réseau.
- La configuration CORS doit rester minimale et contrôlée en production.

### 4.3 Recommandation prioritaire
- Mettre en place une politique de secrets centralisée, avec variables d’environnement injectées par l’orchestrateur ou un outil de gestion de secrets.

## 5. Qualité du code et maintenance

### 5.1 Points forts
- Structure modulaire de l’API backend.
- Présence de tests backend et frontend.
- Pipeline CI/CD présent et assez complet.

### 5.2 Axes d’amélioration
- Renforcer la couverture de tests sur les routes critiques : paiements, archives, uploads, biométrie.
- Ajouter des tests d’intégration autour des services externes (S3, Qdrant, Redis).
- Normaliser les conventions de nommage et la documentation interne sur les modules.

## 6. CI/CD et déploiement

### 6.1 Points forts
- Jenkinsfile structuré avec étapes de lint, tests, build, scan de sécurité et déploiement.
- Docker Compose défini pour orchestrer les services essentiels.
- Les images sont construites séparément pour les frontends et le backend.

### 6.2 Risques
- Le pipeline est complet mais peut être amélioré pour réduire les temps d’exécution et les dépendances répétitives.
- La gestion du fallback `.env.example` en production peut masquer des erreurs de configuration si les secrets ne sont pas injectés correctement.
- Les inspections de sécurité devraient être progressivement renforcées avec des contrôles plus ciblés sur les dépendances, l’image Docker et les secrets.

## 7. Conclusion

Le projet ZoPic Studio est globalement solide et bien orienté produit. La base technique est crédible et la séparation des composants est cohérente. Les améliorations prioritaires concernent principalement la sécurité, la protection des services IA et la robustesse du déploiement.

En l’état, le projet peut être considéré comme une base fonctionnelle et prometteuse, mais il ne devrait pas être considéré comme complètement prêt pour une production critique tant que les recommandations de sécurité et d’opérationnalité ne sont pas mises en œuvre.
