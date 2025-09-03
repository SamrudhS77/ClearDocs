import json
from openai import AzureOpenAI
from app.config import settings
from app.models import NormalizedDoc

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

SYSTEM = """You convert Azure Document Intelligence JSON into a strict normalized JSON.
Only output JSON. Do not include explanations.
Schema:
{schema}
Rules:
- doc_type is "invoice" or "unknown"
- confidence is 0..1 reflecting extraction certainty
- Include a 'trace' map pointing to any span ids or page/line references if present
- Round numeric amounts to 2 decimals
"""

def normalize(ocr_json: dict) -> NormalizedDoc:
    schema = NormalizedDoc.model_json_schema()
    msgs = [
        {"role":"system","content":SYSTEM.format(schema=json.dumps(schema))},
        {"role":"user","content":json.dumps(ocr_json)}
    ]
    # Use Chat Completions for wide availability; temperature 0 for determinism
    resp = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        messages=msgs,
        temperature=0
    )
    content = resp.choices[0].message.content
    data = json.loads(content)
    return NormalizedDoc(**data)
