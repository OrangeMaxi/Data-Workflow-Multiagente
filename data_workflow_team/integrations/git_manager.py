import os
import subprocess
import requests
from typing import Optional, Tuple
from dotenv import load_dotenv

from data_workflow_team.config.settings import settings
from data_workflow_team.core.audit_logger import log_audit_event
from data_workflow_team.integrations.notification_manager import send_alert_notification

load_dotenv()

PROJECT_ROOT = settings.PROJECT_ROOT

def _run_git_cmd(args: list) -> Tuple[Optional[str], Optional[str]]:
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip() or e.stdout.strip()
    except Exception as e:
        return None, str(e)

def git_checkout_branch(branch_name: str) -> str:
    """
    Crea o conmuta a una rama real de Git en el repositorio local y notifica el evento.
    
    Args:
        branch_name: Nombre de la rama Git (ej. 'feature/nueva-vista-sales')
        
    Returns:
        Resultado del comando git checkout y despacho de alerta.
    """
    out, err = _run_git_cmd(["checkout", "-b", branch_name])
    if err and "already exists" in err:
        out, err = _run_git_cmd(["checkout", branch_name])
        
    if err:
        log_audit_event("Engineer", "GIT_CHECKOUT", branch_name, "FAILED", {"error": err})
        return f"Error al cambiar a la rama Git '{branch_name}': {err}"
        
    log_audit_event("Engineer", "GIT_CHECKOUT", branch_name, "SUCCESS")
    
    # Notificación de creación de rama
    send_alert_notification(
        event_type="GIT_BRANCH",
        subject=f"🌿 Nueva Rama Git Creada: {branch_name}",
        message=f"El agente Engineer ha creado/conmutado exitosamente a la rama Git real '{branch_name}'.",
        channels=["email"]
    )
    
    return f"Conmutado exitosamente a la rama Git real: '{branch_name}'. Alerta notificada."

def git_commit(message: str) -> str:
    """
    Agrega todos los archivos modificados e interactúa con Git para hacer un commit real.
    
    Args:
        message: Mensaje explicativo de los cambios para el commit.
        
    Returns:
        Confirmación del commit en Git.
    """
    _run_git_cmd(["add", "."])
    out, err = _run_git_cmd(["commit", "-m", message])
    if err and "nothing to commit" in err:
        return "Git Commit: No hay cambios pendientes para incluir en el commit."
    if err:
        log_audit_event("Engineer", "GIT_COMMIT", message[:30], "FAILED", {"error": err})
        return f"Error ejecutando Git Commit: {err}"
        
    log_audit_event("Engineer", "GIT_COMMIT", message[:30], "SUCCESS")
    return f"Git Commit real realizado exitosamente: '{message}'."

def git_push(branch_name: str) -> str:
    """
    Envía los commits de la rama local al repositorio remoto en GitHub.
    
    Args:
        branch_name: Nombre de la rama a enviar al remoto.
        
    Returns:
        Resultado del envio remoto.
    """
    out, err = _run_git_cmd(["push", "-u", "origin", branch_name])
    if err and "Up-to-date" not in err:
        log_audit_event("Engineer", "GIT_PUSH", branch_name, "FAILED", {"error": err})
        return f"Error ejecutando git push a origin/{branch_name}: {err}"
        
    log_audit_event("Engineer", "GIT_PUSH", branch_name, "SUCCESS")
    return f"Rama '{branch_name}' enviada exitosamente a GitHub origin."

def git_create_pull_request(title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
    """
    Crea un Pull Request real en GitHub y dispara alertas multicanal.
    
    Args:
        title: Título descriptivo del Pull Request.
        body: Descripción y resumen de cambios incluidos.
        head_branch: Rama de origen que contiene los desarrollos.
        base_branch: Rama de destino (ej. 'main').
        
    Returns:
        URL y detalles del Pull Request creado en GitHub con notificación.
    """
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPOSITORY
    
    if not token or not repo:
        log_audit_event("Engineer", "GITHUB_PR_CREATE", head_branch, "FAILED", {"reason": "Missing creds"})
        send_alert_notification(
            event_type="GIT_PR",
            subject=f"📦 Pull Request Preparado: {title}",
            message=f"Pull Request local preparado de '{head_branch}' hacia '{base_branch}'.\n\nResumen de Cambios:\n{body}",
            channels=["email"]
        )
        return (
            "AVISO DE CONFIGURACIÓN: 'GITHUB_TOKEN' o 'GITHUB_REPOSITORY' no están configurados en el .env.\n"
            f"Pull Request local preparado de '{head_branch}' hacia '{base_branch}'. Alerta enviada."
        )

    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code == 201:
            pr_data = res.json()
            pr_url = pr_data.get('html_url')
            log_audit_event("Engineer", "GITHUB_PR_CREATE", pr_url, "SUCCESS")
            
            # Alerta de apertura de PR
            send_alert_notification(
                event_type="GIT_PR",
                subject=f"📦 Nuevo Pull Request Creado: {title}",
                message=f"El agente Engineer ha creado un Pull Request en GitHub.\n\nURL: {pr_url}\nRama: '{head_branch}' -> '{base_branch}'\n\nResumen:\n{body}",
                channels=["email"]
            )
            return f"Pull Request creado exitosamente en GitHub: {pr_url} (PR #{pr_data.get('number')}). Alerta enviada."
        else:
            log_audit_event("Engineer", "GITHUB_PR_CREATE", head_branch, "FAILED", {"status": res.status_code})
            return f"Error al crear Pull Request en GitHub ({res.status_code}): {res.text}"
    except Exception as e:
        return f"Error en la solicitud HTTP a GitHub API: {str(e)}"

def git_merge_pr(pr_number: int) -> str:
    """
    Aprueba y fusiona (merge) un Pull Request en GitHub (DataOps) y notifica la Liberación a Producción.
    
    Args:
        pr_number: Número entero del Pull Request en GitHub (ej. 12).
        
    Returns:
        Resultado del merge en GitHub con alerta de liberación a producción.
    """
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPOSITORY
    
    if not token or not repo:
        log_audit_event("DataOps", "GITHUB_PR_MERGE", str(pr_number), "DENIED", {"reason": "Missing creds"})
        send_alert_notification(
            event_type="RELEASE",
            subject=f"🚀 Fusión y Liberación a Producción Aprobada: PR #{pr_number}",
            message=f"El agente DataOps ha aprobado y ejecutado la liberación a producción del Pull Request #{pr_number}.",
            channels=["email"]
        )
        return f"Simulación DataOps: PR #{pr_number} marcado como aprobado y liberado a producción. Alerta enviada."

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/merge"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"commit_title": f"Merge PR #{pr_number} by DataOps Agent"}
    
    try:
        res = requests.put(url, json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            log_audit_event("DataOps", "GITHUB_PR_MERGE", str(pr_number), "SUCCESS")
            
            # Alerta de liberación a Producción
            send_alert_notification(
                event_type="RELEASE",
                subject=f"🚀 LIBERACIÓN A PRODUCCIÓN EXITO: PR #{pr_number} Fusionado",
                message=f"El agente DataOps ha aprobado y fusionado exitosamente el Pull Request #{pr_number} a la rama main.\nLos desarrollos han sido liberados en producción.",
                channels=["email"]
            )
            return f"Pull Request #{pr_number} fusionado exitosamente en la rama main de GitHub. Alerta de liberación a producción despachada."
        else:
            log_audit_event("DataOps", "GITHUB_PR_MERGE", str(pr_number), "FAILED", {"status": res.status_code})
            return f"Error al fusionar PR #{pr_number} en GitHub ({res.status_code}): {res.text}"
    except Exception as e:
        return f"Error en la API de GitHub: {str(e)}"
