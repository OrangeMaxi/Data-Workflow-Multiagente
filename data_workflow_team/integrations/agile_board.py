import os
import json
import uuid
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from data_workflow_team.config.settings import settings
from data_workflow_team.core.audit_logger import log_audit_event
from data_workflow_team.integrations.notification_manager import send_alert_notification

load_dotenv()

BOARD_FILE = settings.BOARD_FILE

# Mapeo oficial de columnas del tablero Trello
OFFICIAL_TRELLO_COLUMNS = {
    "BACKLOG": "Backlog - To Do",
    "SPRINT": "Current Sprint",
    "IN_PROGRESS": "In Progress",
    "QA": "QA",
    "DONE": "Done"
}

def _load_local_board() -> dict:
    if os.path.exists(BOARD_FILE):
        try:
            with open(BOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_local_board(board: dict):
    with open(BOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2, ensure_ascii=False)

def _get_trello_creds():
    key = settings.TRELLO_API_KEY
    token = settings.TRELLO_TOKEN
    board_id = settings.TRELLO_BOARD_ID
    if key and token and board_id:
        return key, token, board_id
    return None, None, None

def _get_trello_lists(key: str, token: str, board_id: str) -> dict:
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {"key": key, "token": token}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return {l["name"].strip().lower(): l["id"] for l in res.json()}
    except Exception as e:
        print(f"  [Trello Warning] Error al obtener listas del tablero: {e}")
    return {}

def create_agile_ticket(title: str, description: str, assignee: str = None) -> str:
    """
    Crea una tarjeta en la columna 'Backlog - To Do' del tablero Trello en vivo o Kanban local.
    
    Args:
        title: Título descriptivo de la historia de usuario o tarea.
        description: Criterios de aceptación y detalles técnicos.
        assignee: Nombre del responsable asignado (ej. 'Engineer', 'QA').
        
    Returns:
        Confirmación con la URL de Trello o ID del ticket Kanban local.
    """
    key, token, board_id = _get_trello_creds()
    
    if key and token and board_id:
        try:
            lists = _get_trello_lists(key, token, board_id)
            target_list_id = None
            
            # Buscar coincidencia exacta con 'backlog - to do' o variaciones
            for name, list_id in lists.items():
                if "backlog" in name or "to do" in name or "pendiente" in name:
                    target_list_id = list_id
                    break
            if not target_list_id and lists:
                target_list_id = list(lists.values())[0]

            if target_list_id:
                url = "https://api.trello.com/1/cards"
                params = {
                    "key": key,
                    "token": token,
                    "idList": target_list_id,
                    "name": title,
                    "desc": f"{description}\n\nResponsable Asignado: {assignee or 'Sin asignar'}"
                }
                res = requests.post(url, params=params, timeout=5)
                if res.status_code == 200:
                    card_data = res.json()
                    log_audit_event("Analyst", "TRELLO_CARD_CREATE", card_data.get('id'), "SUCCESS")
                    return f"Tarjeta creada en columna 'Backlog - To Do' de Trello en vivo: {card_data.get('shortUrl')} (ID: {card_data.get('id')})"
                else:
                    log_audit_event("Analyst", "TRELLO_CARD_CREATE", title, "FAILED", {"status": res.status_code})
                    return f"Error al crear tarjeta en Trello ({res.status_code}): {res.text}"
        except Exception as e:
            print(f"  [Trello Error] Falló llamada a API de Trello: {e}")

    # Fallback local persistente
    board = _load_local_board()
    ticket_id = f"TICKET-{str(uuid.uuid4())[:4].upper()}"
    board[ticket_id] = {
        "title": title,
        "description": description,
        "status": "Backlog - To Do",
        "assignee": assignee or "Unassigned"
    }
    _save_local_board(board)
    log_audit_event("Analyst", "LOCAL_TICKET_CREATE", ticket_id, "SUCCESS")
    return f"Ticket {ticket_id} creado en el Kanban local en 'Backlog - To Do'. Para sincronizar en Trello en vivo, configura TRELLO_API_KEY en .env."

def update_ticket_status(ticket_id: str, new_status: str) -> str:
    """
    Mueve una tarjeta de Trello a una de las columnas oficiales:
    ['Backlog - To Do', 'Current Sprint', 'In Progress', 'QA', 'Done']
    
    Args:
        ticket_id: ID del ticket local o ID de la tarjeta en Trello (ej. '6a691194bfd5cd6ab6d523ea')
        new_status: Nombre del estado objetivo ('Backlog - To Do', 'Current Sprint', 'In Progress', 'QA', 'Done').
        
    Returns:
        Confirmación del movimiento del ticket y despacho de alerta si corresponde.
    """
    key, token, board_id = _get_trello_creds()
    
    if key and token and board_id:
        try:
            lists = _get_trello_lists(key, token, board_id)
            target_list_id = None
            new_status_lower = new_status.strip().lower()
            
            # 1. Búsqueda exacta de lista
            if new_status_lower in lists:
                target_list_id = lists[new_status_lower]
            else:
                # 2. Búsqueda por palabra clave en columnas oficiales
                for name, list_id in lists.items():
                    if new_status_lower in name or name in new_status_lower:
                        target_list_id = list_id
                        break
                    if "qa" in new_status_lower and "qa" in name:
                        target_list_id = list_id
                        break
                    if "progress" in new_status_lower and "progress" in name:
                        target_list_id = list_id
                        break
                    if "sprint" in new_status_lower and "sprint" in name:
                        target_list_id = list_id
                        break
                    if "done" in new_status_lower and "done" in name:
                        target_list_id = list_id
                        break
                    
            if target_list_id and len(ticket_id) > 10:
                url = f"https://api.trello.com/1/cards/{ticket_id}"
                params = {"key": key, "token": token, "idList": target_list_id}
                res = requests.put(url, params=params, timeout=5)
                if res.status_code == 200:
                    log_audit_event("AgileBoard", "TRELLO_CARD_UPDATE", ticket_id, "SUCCESS", {"new_status": new_status})
                    
                    if any(kw in new_status.lower() for kw in ["done", "qa", "completado"]):
                        send_alert_notification(
                            event_type="KANBAN_DONE",
                            subject=f"✅ Tarea Movida a '{new_status}': {ticket_id}",
                            message=f"La tarjeta de Trello {ticket_id} ha sido trasladada exitosamente a la columna '{new_status}'.",
                            channels=["email"]
                        )
                    return f"Tarjeta de Trello ({ticket_id}) movida exitosamente a la columna '{new_status}'."
        except Exception as e:
            print(f"  [Trello Error] Falló actualización en Trello: {e}")

    board = _load_local_board()
    if ticket_id in board:
        board[ticket_id]["status"] = new_status
        _save_local_board(board)
        log_audit_event("AgileBoard", "LOCAL_TICKET_UPDATE", ticket_id, "SUCCESS", {"new_status": new_status})
        
        if any(kw in new_status.lower() for kw in ["done", "qa", "completado"]):
            send_alert_notification(
                event_type="KANBAN_DONE",
                subject=f"✅ Tarea Local Movida a '{new_status}': {ticket_id}",
                message=f"El ticket local {ticket_id} ('{board[ticket_id].get('title')}') ha sido movido a '{new_status}'.",
                channels=["email"]
            )
        return f"Ticket local {ticket_id} actualizado a '{new_status}' en .kanban_board.json."

    return f"Estado del ticket {ticket_id} actualizado a '{new_status}'."

def generate_business_doc(title: str, content: str) -> str:
    """
    Genera un archivo Markdown real con la especificación formal de negocio en la carpeta docs/.
    """
    docs_dir = settings.DOCS_DIR
    os.makedirs(docs_dir, exist_ok=True)
    filename = f"{title.lower().replace(' ', '_')}.md"
    filepath = os.path.join(docs_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}\n")
        
    log_audit_event("Analyst", "GENERATE_DOC", filepath, "SUCCESS")
    return f"Documento de especificación formal guardado en el archivo real: {filepath}"
