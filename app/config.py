import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    AZURE_DI_ENDPOINT: str = os.environ["AZURE_DI_ENDPOINT"]
    AZURE_DI_KEY: str = os.environ["AZURE_DI_KEY"]
    AZURE_OPENAI_ENDPOINT: str = os.environ["AZURE_OPENAI_ENDPOINT"]
    OPENAI_API_VERSION: str = os.environ["OPENAI_API_VERSION"]
    AZURE_OPENAI_KEY: str = os.environ["AZURE_OPENAI_KEY"]
    AZURE_OPENAI_DEPLOYMENT: str = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    STORAGE_DIR: str = os.environ.get("STORAGE_DIR", "outputs")
    HITL_ENABLED: bool = os.environ.get("HITL_ENABLED", "true").lower() == "true"
    CONFIDENCE_THRESHOLD: float = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.85"))

settings = Settings()