#!/usr/bin/env bash
set -euo pipefail

node_is_supported() {
  command -v node >/dev/null 2>&1 || return 1
  local major
  major="$(node -p 'Number(process.versions.node.split(".")[0])')"
  [[ "$major" -ge 20 ]]
}

if node_is_supported; then
  exec npm "$@"
fi

nvm_directory="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$nvm_directory/nvm.sh" ]]; then
  # shellcheck disable=SC1090
  source "$nvm_directory/nvm.sh"
  nvm use --silent
fi

if ! node_is_supported; then
  printf "Rune precisa do Node.js 20 ou mais recente. Rode 'nvm install' nesta pasta.\n" >&2
  exit 1
fi

exec npm "$@"
