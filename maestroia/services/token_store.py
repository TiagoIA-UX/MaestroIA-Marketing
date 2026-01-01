from pathlib import Path
import json
from typing import Optional

STORE = Path(__file__).resolve().parent.parent / 'data' / 'tokens.json'
STORE.parent.mkdir(parents=True, exist_ok=True)


def load_store() -> dict:
    if not STORE.exists():
        return {}
    try:
        return json.loads(STORE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_store(data: dict):
    STORE.write_text(json.dumps(data, indent=2), encoding='utf-8')


def save_token(provider: str, user_key: str, token_data: dict):
    data = load_store()
    data.setdefault(provider, {})
    data[provider][user_key] = token_data
    save_store(data)


def get_token(provider: str, user_key: str) -> Optional[dict]:
    data = load_store()
    return data.get(provider, {}).get(user_key)
