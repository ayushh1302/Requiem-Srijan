import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

# App Info
APP_NAME = "ClauseClear"
APP_VERSION = "1.0.0"
HACKATHON_NAME = "Srijan Hackathon - GH Raisoni College of Engineering and Management, Pune"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

# Demo Mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

# Server Config
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))

# Directories
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DIR", "data/chroma_db")
SQLITE_DB_PATH = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/clauseclear.db")
SAMPLE_CONTRACTS_DIR = BASE_DIR / "sample_contracts"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

# Upload constraints
MAX_FILE_SIZE_MB = 15
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
