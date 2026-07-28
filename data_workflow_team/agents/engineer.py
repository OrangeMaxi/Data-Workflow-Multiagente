import os
from google.adk.agents import Agent
from data_workflow_team.config.settings import settings
from data_workflow_team.integrations.data_connectors import (
    execute_data_mutation_query,
    execute_read_only_query,
    file_system_operations,
    install_python_package,
    databricks_volume_operations,
    databricks_pipeline_operations
)
from data_workflow_team.integrations.git_manager import (
    git_checkout_branch,
    git_commit,
    git_push,
    git_create_pull_request
)
from data_workflow_team.integrations.notification_manager import send_alert_notification

def _get_active_env_summary() -> str:
    conns = []
    if settings.DATABRICKS_HOST:
        conns.append(f"- Databricks SDK & SQL (Host: {settings.DATABRICKS_HOST}) [LIBRE ACCESO A TABLAS, VISTAS, VOLÚMENES Y PIPELINES]")
    if settings.GITHUB_TOKEN:
        conns.append(f"- GitHub (Repo: {settings.GITHUB_REPOSITORY or 'N/A'}) [AUTENTICADO]")
    if settings.TRELLO_API_KEY:
        conns.append(f"- Trello (Board: {settings.TRELLO_BOARD_ID or 'N/A'}) [CONECTADO]")
    return "\n".join(conns) if conns else "- Ninguna credencial remota en .env"

engineer_agent = Agent(
    name="Engineer",
    model="gemini-2.5-flash",
    description=(
        "Ingeniero de Datos y Desarrollador ETL. "
        "Especializado en GITOPS, NOTIFICACIONES Y ESCRITURA EN DATABRICKS: Aplica las mejores prácticas de ingeniería de datos. "
        "Guarda las definiciones SQL en archivos locales, crea ramas Git ('feature/...'), realiza commits, envía a GitHub, "
        "abre el Pull Request ('git_create_pull_request') y dispara alertas multicanal ('send_alert_notification') a maximilianonaranjo@gmail.com."
    ),
    instruction=(
        "Eres el Ingeniero de Datos del equipo. Aplicas STRICT GITOPS Y LAS MEJORES PRÁCTICAS DE SOFTWARE Y DATOS.\n\n"
        "RECURSOS ACTIVOS:\n"
        f"{_get_active_env_summary()}\n\n"
        "FLUJO OBLIGATORIO DE INGENIERÍA Y GITOPS (DATABRICKS / BBDD):\n"
        "1. CREACIÓN DE RAMA GIT: Al recibir un requerimiento de nueva vista/tabla/pipeline, crea una rama 'git_checkout_branch' (ej. `feature/vista-resumen-franquicias`).\n"
        "2. PERSISTENCIA EN CÓDIGO (IaC): Guarda el script SQL o código de la vista en un archivo local usando 'file_system_operations' (ej. `models/views/gold_resumen_franquicias.sql`).\n"
        "3. EJECUCIÓN EN DATABRICKS: Aplica los cambios en Databricks con 'execute_data_mutation_query' o la herramienta correspondiente.\n"
        "4. CONTROL DE VERSIONES Y PULL REQUEST: Guarda los cambios con 'git_commit', haz 'git_push' a origin y abre el Pull Request en GitHub con 'git_create_pull_request'.\n"
        "5. NOTIFICACIONES Y ALERTAS: Usa 'send_alert_notification' para informar por correo (maximilianonaranjo@gmail.com) o chat los hitos clave alcanzados."
    ),
    tools=[
        execute_data_mutation_query,
        execute_read_only_query,
        file_system_operations,
        databricks_volume_operations,
        databricks_pipeline_operations,
        install_python_package,
        git_checkout_branch,
        git_commit,
        git_push,
        git_create_pull_request,
        send_alert_notification
    ]
)
