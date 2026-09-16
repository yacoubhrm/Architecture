# Abdellah Moutal

Site vitrine Vite pour Abdellah Moutal — défenseur central / milieu défensif, FC Tevragh Zeina (Super D1).

## Développement

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Déploiement Firebase Hosting

```bash
# Authentification (une fois)
npx firebase login

# Créer le projet Firebase si besoin, puis :
npx firebase use --add
npm run deploy
```

Le site est servi depuis le dossier `dist` (voir `firebase.json`).
