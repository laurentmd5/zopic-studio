# ZoPic Studio - App Athlètes (PWA)

Cette application mobile-first (PWA) construite avec React/Vite est conçue pour les **athlètes**.
Elle permet de :
- Trouver des photos de soi via un simple selfie (IA Biométrique).
- Acheter ses photos (Paiement local).
- Personnaliser son Profil Public "Identité Sportive" et sa Galerie.

## Démarrage Rapide

```bash
npm install
npm run dev
```

## Particularités
- **Bottom Navigation** : Interface optimisée pour mobile (Accueil, Recherche, Achats, Profil).
- **Profil Public & SSR** : Le partage du profil athlète (`/@pseudo`) repose sur un backend SSR léger (intégré au main.py FastAPI) qui pré-génère les balises Open Graph pour le SEO, puis hydrate cette application React.

Pour plus d'informations sur l'architecture globale, voir le dossier `/docs` à la racine.
