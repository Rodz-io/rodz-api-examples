"""Tiny helper shared by the examples: reads RODZ_API_KEY and calls the Rodz API."""

import os
import pathlib
import sys

import requests

BASE_URL = os.environ.get("RODZ_BASE_URL", "https://api.rodz.io")
ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_dotenv():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def api_key():
    _load_dotenv()
    key = os.environ.get("RODZ_API_KEY")
    if not key:
        sys.exit("Set RODZ_API_KEY (copy .env.example to .env and paste your key).")
    return key


def rodz(method, path, **kwargs):
    """Call the API and return the JSON body. Raises on 4xx/5xx with the API's error message."""
    resp = requests.request(
        method,
        BASE_URL + path,
        headers={"Authorization": f"Bearer {api_key()}"},
        timeout=60,
        **kwargs,
    )
    if resp.status_code == 429:
        sys.exit(f"Rate limited, retry after {resp.headers.get('Retry-After', '1')} s")
    if not resp.ok:
        sys.exit(f"{resp.status_code}: {resp.text}")
    return resp.json()
