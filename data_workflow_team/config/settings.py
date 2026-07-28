import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class SystemSettings:
    """Configuración centralizada de nivel empresarial para el Data Workflow Multiagente."""
    
    # Directorios y Rutas
    PROJECT_ROOT: Path = PROJECT_ROOT
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    DOCS_DIR: Path = PROJECT_ROOT / "docs"
    BOARD_FILE: Path = PROJECT_ROOT / ".kanban_board.json"
    
    # Credenciales de Servicios
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN", "")
    DATABRICKS_HTTP_PATH: str = os.getenv("DATABRICKS_HTTP_PATH", "")
    
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPOSITORY: str = os.getenv("GITHUB_REPOSITORY", "")
    
    TRELLO_API_KEY: str = os.getenv("TRELLO_API_KEY", "")
    TRELLO_TOKEN: str = os.getenv("TRELLO_TOKEN", "")
    TRELLO_BOARD_ID: str = os.getenv("TRELLO_BOARD_ID", "")
    
    # Notificaciones y Alertas Multicanal
    NOTIFICATION_EMAIL_TO: str = os.getenv("NOTIFICATION_EMAIL_TO", "maximilianonaranjo@gmail.com")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    GENERIC_WEBHOOK_URL: str = os.getenv("GENERIC_WEBHOOK_URL", "")
    
    # Parámetros de Operación
    MAX_CONNECTIVITY_RETRIES: int = 3
    DEFAULT_QUERY_ROW_LIMIT: int = 100
    SAFE_MODE_MUTATIONS: bool = True

settings = SystemSettings()
