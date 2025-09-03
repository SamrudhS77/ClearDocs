from pathlib import Path
from app.config import settings

BASE = Path(settings.STORAGE_DIR)
BASE.mkdir(parents=True, exist_ok=True)

def save_bytes(relpath: str, data: bytes) -> str:
    p = BASE / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return str(p)

def save_json(relpath: str, obj: dict) -> str:
    import json
    p = BASE / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return str(p)
