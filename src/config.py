import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHROME_CDP_URL: str = os.getenv("CHROME_CDP_URL", "http://localhost:9222")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    STRAPI_API_URL: str = os.getenv("STRAPI_API_URL", "https://admin.chaldea.foundation")
    STRAPI_API_TOKEN: str = os.getenv("STRAPI_API_TOKEN", "")
    
    DEFAULT_RESUME_JSON_ENDPOINT: str = os.getenv(
        "DEFAULT_RESUME_JSON_ENDPOINT",
        "https://admin.chaldea.foundation/api/updated-resume?populate=*"
    )
    DEFAULT_RESUME_PDF_URL: str = os.getenv(
        "DEFAULT_RESUME_PDF_URL",
        "https://admin.chaldea.foundation/uploads/gonzalo_salvador_corvalan_Resume_fe85477412.pdf"
    )
    
    AUTONOMY_MODE: str = os.getenv("AUTONOMY_MODE", "semi-autonomous").lower()
    TEMP_DIR: Path = ROOT_DIR / os.getenv("TEMP_DIR", "temp_resumes")

settings = Settings()
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
