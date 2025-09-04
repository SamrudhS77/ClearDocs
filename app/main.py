from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import json

from app.config import settings
from app.azure_di import analyze_invoice_or_general
from app.llm_validate import normalize
from app.business_rules import compute_confidence, validate_business_rules
from app.governance import (
    new_run_id, write_audit, sha256_bytes, pii_redact
)
from app.storage import save_bytes, save_json

app = FastAPI(title="Invoice IDP (Azure)")

@app.get("/health")
def health(): return {"ok": True}

@app.post("/extract")
# Validate input
async def extract(file: UploadFile, hitl: bool = True):
    if not file.filename.lower().endswith((".pdf",".png",".jpg",".jpeg","tiff","tif")):
        raise HTTPException(400, "Unsupported file type")
# Generate run ID and hash file
    run_id = new_run_id()
    raw = await file.read()
    fhash = sha256_bytes(raw)
    rel = f"ingest/{run_id}_{file.filename}"
    local_path = save_bytes(rel, raw)
# Audit log
    write_audit("INGEST", {"file": file.filename, "bytes": len(raw), "sha256": fhash}, run_id)
# OCR with Azure DI
    used_model, ocr_json = analyze_invoice_or_general(raw)
    write_audit("EXTRACT", {"used_model": used_model, "pages": len(ocr_json.get("pages", []))}, run_id)
    save_json(f"artifacts/{run_id}_ocr.json", ocr_json)
# Normalize with LLM
    norm = normalize(ocr_json)
    # Recompute/override confidence with deterministic business metric
    norm.confidence = compute_confidence(norm)
    errors = validate_business_rules(norm)
# Audit log for LLM
    write_audit("LLM", {
        "deployment": settings.AZURE_OPENAI_DEPLOYMENT,
        "confidence": norm.confidence,
        "errors": errors
    }, run_id)

# Decide HITL
    if hitl and (norm.confidence < settings.CONFIDENCE_THRESHOLD or errors):
        write_audit("HITL_ENQUEUE", {"reason": "low_conf_or_errors", "errors": errors}, run_id)
        return {"status":"queued_for_review","run_id": run_id, "confidence": norm.confidence, "errors": errors}

# Emit redacted JSON
    redacted = pii_redact(norm.model_dump())
    out_path = save_json(f"results/{run_id}.json", redacted)
    write_audit("EMIT", {"output": out_path, "confidence": norm.confidence}, run_id)

    return {"status":"ok","run_id": run_id, "confidence": norm.confidence, "output": out_path}
