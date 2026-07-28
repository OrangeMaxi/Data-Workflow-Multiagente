import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
AUDIT_LOG_FILE = LOGS_DIR / "audit.log"

os.makedirs(LOGS_DIR, exist_ok=True)

logger = logging.getLogger("enterprise_audit")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def log_audit_event(agent_name: str, action_type: str, target: str, status: str, details: dict = None) -> str:
    """
    Registra un evento de auditoría de seguridad inmutable en formato JSON en logs/audit.log.
    
    Args:
        agent_name: Nombre del agente que ejecuta la acción (ej. 'Engineer', 'DataOps')
        action_type: Tipo de operación (ej. 'DATABRICKS_DDL', 'GIT_PR_MERGE', 'TRELLO_CARD_CREATE')
        target: Recurso objetivo (ej. 'bakehouse.sales_customers', 'repo/main')
        status: Resultado del evento ('SUCCESS', 'FAILED', 'DENIED')
        details: Payload adicional con detalles de la operación.
        
    Returns:
        Cadena con la confirmación de registro de auditoría.
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "action": action_type,
        "target": target,
        "status": status,
        "details": details or {}
    }
    
    log_line = json.dumps(event, ensure_ascii=False)
    logger.info(log_line)
    print(f"  [Audit Log] [{status}] {agent_name} -> {action_type} on {target}")
    return f"Audit log registrado: {event['timestamp']}"
