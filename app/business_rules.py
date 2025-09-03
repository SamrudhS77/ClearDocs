from app.models import NormalizedDoc

def compute_confidence(doc: NormalizedDoc) -> float:
    # Basic recipe: field presence + consistency checks
    score = 0.5
    if doc.invoice_number: score += 0.1
    if doc.invoice_date:   score += 0.1
    if doc.total_amount:   score += 0.1
    if doc.currency:       score += 0.05
    if doc.line_items:     score += 0.1
    # Totals check
    try:
        line_sum = round(sum(li.amount or 0 for li in doc.line_items), 2)
        if doc.total_amount and abs((doc.total_amount or 0) - line_sum) <= 0.05:
            score += 0.05
    except Exception:
        pass
    return min(score, 1.0)

def validate_business_rules(doc: NormalizedDoc) -> list[str]:
    errors = []
    if doc.total_amount is not None:
        try:
            line_sum = round(sum(li.amount or 0 for li in doc.line_items), 2)
            if abs(doc.total_amount - line_sum) > 0.05:
                errors.append(f"Total {doc.total_amount} != sum(line_items) {line_sum}")
        except Exception:
            errors.append("Failed to compute line items sum")
    return errors
