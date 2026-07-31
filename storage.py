import json
import os
from threading import Lock

from config import DATA_FILE, DEFAULT_FORMAT, DEFAULT_QUALITY

_lock = Lock()


def _default_user() -> dict:
    return {
        "format": DEFAULT_FORMAT,
        "quality": DEFAULT_QUALITY,
        "history": [],
        "stats": {"downloaded": 0},
    }


def _ensure_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _load() -> dict:
    _ensure_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id: int) -> dict:
    with _lock:
        data = _load()
        user = data.get(str(user_id))
        if user is None:
            user = _default_user()
            data[str(user_id)] = user
            _save(data)
        return user


def set_user_setting(user_id: int, key: str, value):
    with _lock:
        data = _load()
        user = data.setdefault(str(user_id), _default_user())
        user[key] = value
        _save(data)


def add_history(user_id: int, title: str, url: str):
    with _lock:
        data = _load()
        user = data.setdefault(str(user_id), _default_user())
        user["history"].insert(0, {"title": title, "url": url})
        user["history"] = user["history"][:20]
        user["stats"]["downloaded"] = user["stats"].get("downloaded", 0) + 1
        _save(data)
