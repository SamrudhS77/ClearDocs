from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.config import settings

client = DocumentIntelligenceClient(
    endpoint=settings.AZURE_DI_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_DI_KEY)
)

def analyze_invoice_or_general(file_bytes: bytes) -> tuple[str, dict]:
    """
    Try prebuilt-invoice first; if it throws or yields no reasonable fields, fallback to prebuilt-document.
    Return (used_model, result_dict)
    """
    try:
        poller = client.begin_analyze_document("prebuilt-invoice", file_bytes)
        result = poller.result()
        if result and getattr(result, "documents", []):
            return "prebuilt-invoice", result.to_dict()
    except Exception:
        pass

    poller = client.begin_analyze_document("prebuilt-document", file_bytes)
    result = poller.result()
    return "prebuilt-document", result.to_dict()
