import hashlib, json, time, uuid
from pathlib import Path
from typing import Any, Dict
from app.config import settings
from app.storage import save_json

AUDIT_DIR = "audit"

SENSITIVE_KEYS = {"account_number","iban","swift","tax_id","abn","pan","bsb"}

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def pii_redact(obj: Any):
    if isinstance(obj, dict):
        return {k: ("***REDACTED***" if k.lower() in SENSITIVE_KEYS else pii_redact(v)) for k,v in obj.items()}
    if isinstance(obj, list):
        return [pii_redact(x) for x in obj]
    return obj

def write_audit(kind: str, payload: Dict[str, Any], run_id: str):
    payload = dict(payload)
    payload["ts_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_json(f"{AUDIT_DIR}/{run_id}_{kind}.json", payload)

def new_run_id() -> str:
    return uuid.uuid4().hex[:12]
