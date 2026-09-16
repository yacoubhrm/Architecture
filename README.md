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

## Lien public actuel

https://raw.githack.com/yacoubhrm/Architecture/gh-pages/index.html

(copie CDN de la branche `gh-pages`)

## Publication

Le site est compilé dans `dist/` (`firebase.json` + GitHub Pages).

### GitHub Pages

Le workflow `.github/workflows/github-pages.yml` publie `dist/` via Actions.
URL attendue : `https://yacoubhrm.github.io/Architecture/`

### Firebase Hosting

Projet cible : `abdellah-moutal` → `https://abdellah-moutal.web.app`

```bash
npx firebase-tools login:ci
# Ajouter le token comme secret FIREBASE_TOKEN (GitHub Actions et/ou Cloud Agent)
npm run deploy
```

Le workflow `.github/workflows/firebase-deploy.yml` utilise `secrets.FIREBASE_TOKEN`.
