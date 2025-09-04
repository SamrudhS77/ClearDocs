from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from app.config import settings
import json

client = DocumentIntelligenceClient(
    endpoint=settings.AZURE_DI_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_DI_KEY)
)

CANDIDATE_MODELS = [
    "prebuilt-invoice",
    "prebuilt-document",
    "prebuilt-layout",
    "prebuilt-read",
]

def _result_to_dict(analyze_result) -> dict:
    """
    Convert AnalyzeResult to a plain dict across SDK versions.
    Tries several known serialization shapes before falling back to a generic JSON dump.
    """
    # 1) Newer/older SDKs sometimes expose one of these:
    for attr in ("to_dict", "as_dict", "model_dump", "to_json"):
        if hasattr(analyze_result, attr):
            val = getattr(analyze_result, attr)
            try:
                out = val() if callable(val) else val
                if isinstance(out, dict):
                    return out
                if isinstance(out, str):
                    return json.loads(out)
            except Exception:
                pass

    # 2) Try Pydantic-style JSON if present
    for attr in ("model_dump_json",):
        if hasattr(analyze_result, attr):
            try:
                return json.loads(getattr(analyze_result, attr)())
            except Exception:
                pass

    # 3) Last-resort: generic JSON fallback via default serializer
    try:
        return json.loads(json.dumps(analyze_result, default=lambda o: getattr(o, "__dict__", str(o))))
    except Exception:
        # If absolutely everything fails, at least return a string repr
        return {"analyze_result": str(analyze_result)}

def analyze_invoice_or_general(file_bytes: bytes) -> tuple[str, dict]:
    print(f"[DI] Using endpoint: {settings.AZURE_DI_ENDPOINT}")
    last_err = None

    for model_id in CANDIDATE_MODELS:
        try:
            poller = client.begin_analyze_document(model_id, file_bytes)
            result = poller.result()
            result_dict = _result_to_dict(result)
            return model_id, result_dict
        except HttpResponseError as e:
            last_err = e
        except Exception as e:
            last_err = e

    raise RuntimeError(f"Document Intelligence analysis failed. Last error: {last_err}")
