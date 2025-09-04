import sys, json
from pathlib import Path
from app.azure_di import analyze_invoice_or_general
from app.llm_validate import normalize
from app.business_rules import compute_confidence, validate_business_rules
from app.governance import pii_redact

if __name__ == "__main__":
    p = Path(sys.argv[1])
    raw = p.read_bytes()
    used, ocr = analyze_invoice_or_general(raw)
    norm = normalize(ocr)
    norm.confidence = compute_confidence(norm)
    errors = validate_business_rules(norm)
    print(json.dumps({
        "used_model": used,
        "confidence": norm.confidence,
        "errors": errors,
        "result": pii_redact(norm.model_dump())
    }, indent=2))
