import os
from dotenv import load_dotenv
from pathlib import Path

# =========================
# CARREGAMENTO DO .ENV
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# =========================
# AMBIENTE
# =========================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

IS_PRODUCTION = ENVIRONMENT == "production"

# =========================
# OPENAI / LLM
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))

if not OPENAI_API_KEY:
    raise RuntimeError(
        "❌ OPENAI_API_KEY não encontrada. "
        "Verifique o arquivo .env na raiz do projeto."
    )

# =========================
# LIMITES E GOVERNANÇA
# =========================

MAX_CAMPAIGNS_PER_USER = int(os.getenv("MAX_CAMPAIGNS_PER_USER", "3"))
REQUIRE_HUMAN_APPROVAL = os.getenv("REQUIRE_HUMAN_APPROVAL", "true").lower() == "true"

# =========================
# LOGS
# =========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =========================
# DEBUG (SÓ PARA DEV)
# =========================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
