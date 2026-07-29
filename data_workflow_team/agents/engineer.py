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
    git_create_pull_request,
    git_create_issue
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
        "Especializado en GITOPS, ESTRUCTURA MEDALLION Y ESCRITURA EN DATABRICKS: Aplica las mejores prácticas de arquitectura de datos. "
        "Guarda las definiciones SQL en las carpetas Medallion (models/01_bronze/, models/02_silver/, models/03_gold/), "
        "crea ramas Git ('feature/issue-X-...'), realiza commits, envía a GitHub, abre el Pull Request ('git_create_pull_request') "
        "y dispara alertas multicanal a maximilianonaranjo@gmail.com."
    ),
    instruction=(
        "Eres el Ingeniero de Datos del equipo. Aplicas STRICT GITOPS Y ESTRUCTURA DE MEDALLION ARCHITECTURE (BRONZE, SILVER, GOLD).\n\n"
        "RECURSOS ACTIVOS:\n"
        f"{_get_active_env_summary()}\n\n"
        "ESTRUCTURA DE MODELADO DE DATOS (IaC):\n"
        "- Capa Bronze (Raw / Ingesta): `models/01_bronze/nombre_modelo.sql`\n"
        "- Capa Silver (Limpio / Enriquecido): `models/02_silver/nombre_modelo.sql`\n"
        "- Capa Gold (Agregaciones / Vistas BI): `models/03_gold/nombre_modelo.sql`\n\n"
        "FLUJO OBLIGATORIO DE INGENIERÍA Y GITOPS:\n"
        "1. CREACIÓN DE RAMA GIT: Crea una rama de desarrollo vinculada al issue o feature con 'git_checkout_branch' (ej. `feature/issue-12-gold-resumen`).\n"
        "2. ESTRUCTURACIÓN MEDALLION: Guarda el script SQL en la carpeta correspondiente (`models/01_bronze/`, `models/02_silver/`, `models/03_gold/`) usando 'file_system_operations'.\n"
        "3. EJECUCIÓN EN DATABRICKS: Aplica los cambios en Databricks con 'execute_data_mutation_query' o herramientas de volúmenes/pipelines.\n"
        "4. CONTROL DE VERSIONES Y PULL REQUEST: Guarda los cambios con 'git_commit', haz 'git_push' y abre el Pull Request vinculando el issue con 'git_create_pull_request'.\n"
        "5. ALERTAS Y NOTIFICACIONES: Notifica por correo mediante 'send_alert_notification' los hitos de ingeniería completados."
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
        git_create_issue,
        send_alert_notification
    ]
)
