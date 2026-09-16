#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT_ID="abdellah-moutal"
DISPLAY_NAME="Abdellah Moutal"

npm run build

if [[ -n "${FIREBASE_TOKEN:-}" ]]; then
  AUTH_ARGS=(--token "$FIREBASE_TOKEN")
else
  AUTH_ARGS=()
fi

echo "→ Creating Firebase project: $PROJECT_ID"
npx firebase projects:create "$PROJECT_ID" --display-name "$DISPLAY_NAME" "${AUTH_ARGS[@]}" || {
  echo "Project may already exist — continuing"
}

echo "→ Selecting project"
npx firebase use "$PROJECT_ID" "${AUTH_ARGS[@]}"

# Ensure default hosting site exists (same name as project)
npx firebase hosting:sites:create "$PROJECT_ID" "${AUTH_ARGS[@]}" 2>/dev/null || true
npx firebase target:apply hosting "$PROJECT_ID" "$PROJECT_ID" "${AUTH_ARGS[@]}" 2>/dev/null || true

echo "→ Deploying Hosting"
npx firebase deploy --only hosting --project "$PROJECT_ID" "${AUTH_ARGS[@]}" --non-interactive

echo "✓ Live: https://${PROJECT_ID}.web.app"
