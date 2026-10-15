# Sourced by every script here: loads RODZ_API_KEY from ../.env if it is not already set.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "${RODZ_API_KEY:-}" ] && [ -f "$HERE/../.env" ]; then
  set -a; . "$HERE/../.env"; set +a
fi
: "${RODZ_API_KEY:?Set RODZ_API_KEY (copy .env.example to .env and paste your key)}"
RODZ_BASE_URL="${RODZ_BASE_URL:-https://api.rodz.io}"
SIGNALS_DIR="$HERE/../signals"
