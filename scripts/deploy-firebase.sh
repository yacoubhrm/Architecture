#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
npm run build
if [[ -z "${FIREBASE_TOKEN:-}" ]]; then
  echo "Connectez Firebase: npx firebase login"
  npx firebase deploy --only hosting
else
  npx firebase deploy --only hosting --token "$FIREBASE_TOKEN"
fi
