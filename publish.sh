#!/usr/bin/env bash
# Build, validate and publish only the independent scene-report repository.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export GIT_TERMINAL_PROMPT=0

case "${1:-}" in
  --help|-h)
    printf '%s\n' 'Usage: ./publish.sh [commit message]' '       ./publish.sh --check' 'Checks and publishes the existing report content. Does not update experiment evidence.'
    exit 0
    ;;
esac

if [[ "$(git rev-parse --show-toplevel)" != "$PWD" ]]; then
  printf '%s\n' 'Run this script from its own independent report repository.' >&2
  exit 1
fi
if [[ "$(git branch --show-current)" != main ]]; then
  printf '%s\n' 'Publishing requires the main branch. No branch was changed.' >&2
  exit 1
fi
expected='git@github.com:chilazy01-blip/chilazy01-blip.github.io.git'
if [[ "$(git remote get-url --push origin)" != "$expected" ]]; then
  printf '%s\n' 'Unexpected push destination. Configure this repository deployment key first.' >&2
  exit 1
fi
# Do not accidentally include files staged for a different purpose.
while IFS= read -r -d '' file; do
  case "$file" in
    .gitignore|README.md|build.py|publish.sh|.github/workflows/pages.yml|content/*|public/*|checks/static.py) ;;
    *) printf 'Unexpected staged file: %s\n' "$file" >&2; exit 1 ;;
  esac
done < <(git diff --cached --name-only -z)

python3 -I -B build.py
python3 -I -B checks/static.py
git diff --check
if [[ "${1:-}" == --check ]]; then
  printf '%s\n' 'Local checks passed. No commit, push or remote change was made.'
  exit 0
fi

# Require a fast-forward; never reset, force-push or silently overwrite web edits.
git fetch --no-tags origin main
if ! git merge-base --is-ancestor FETCH_HEAD HEAD; then
  printf '%s\n' 'GitHub contains commits absent locally. Merge those changes before publishing; nothing was overwritten.' >&2
  exit 1
fi
# Verify key access before making a local commit.
if ! git push --dry-run origin HEAD:main; then
  printf '%s\n' 'Push preflight failed. Check repository Deploy keys (Allow write access), branch rules and network access.' >&2
  exit 1
fi

git add -- .gitignore README.md build.py publish.sh .github/workflows/pages.yml content public checks/static.py
if ! git diff --cached --quiet; then
  git diff --cached --check
  git commit -m "${1:-Update scene progress report}"
fi
git push origin HEAD:main
printf '%s\n' 'Pushed. GitHub Actions must finish successfully before the website is updated.' 'Deployment: https://github.com/chilazy01-blip/chilazy01-blip.github.io/actions' 'Website: https://chilazy01-blip.github.io/'
