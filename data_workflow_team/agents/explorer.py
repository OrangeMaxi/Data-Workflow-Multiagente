import os
from google.adk.agents import Agent
from data_workflow_team.config.settings import settings
from data_workflow_team.integrations.data_connectors import connect_to_universal_source, execute_read_only_query, install_python_package

def _get_active_env_summary() -> str:
    conns = []
    if settings.DATABRICKS_HOST:
        conns.append(f"- Databricks SQL Warehouse (Host: {settings.DATABRICKS_HOST}) [CONECTOR MULTISCHEMA ACTIVO]")
    if settings.GITHUB_TOKEN:
        conns.append(f"- GitHub (Repo: {settings.GITHUB_REPOSITORY or 'N/A'}) [AUTENTICADO]")
    if settings.TRELLO_API_KEY:
        conns.append(f"- Trello Kanban (Board: {settings.TRELLO_BOARD_ID or 'N/A'}) [CONECTADO]")
    return "\n".join(conns) if conns else "- Ninguna credencial remota en .env"

explorer_agent = Agent(
    name="Explorer",
    model="gemini-2.5-flash",
    description=(
        "Explorador e Investigador de Datos (EDA - Exploratory Data Analysis). "
        "Especializado en SOLO LECTURA: inspecciona esquemas (SHOW SCHEMAS), descubre tablas, "
        "ejecuta consultas SELECT cruzadas y analiza la calidad estructural de los datos en Databricks, PostgreSQL, MySQL o CSV."
    ),
    instruction=(
        "Eres el Explorador de Datos del equipo. Tu rol es exclusivamente de SOLO LECTURA para investigación e inspección.\n\n"
        "SERVICIOS CONECTADOS:\n"
        f"{_get_active_env_summary()}\n\n"
        "REGLAS OBLIGATORIAS:\n"
        "1. LECTURA Y MULTISCHEMA: Inspecciona todos los esquemas y tablas reales usando 'connect_to_universal_source' o consultas SELECT con 'execute_read_only_query'.\n"
        "2. RE-ENRUTAMIENTO OBLIGATORIO DE ESCRITURA: Si la solicitud implica crear, modificar o eliminar tablas/vistas (CREATE TABLE, CREATE VIEW, ALTER, DROP), "
        "NO intentes ejecutarlo. Informa al Orquestador/usuario que la creación y escritura corresponde al 'Engineer'.\n"
        "3. MANEJO DE ERRORES: Analiza autónomamente los mensajes de error técnicos (ej. HTTP 404, credenciales) e indica la causa exacta.\n"
        "4. CONTROLADORES: Si la herramienta indica 'PERMISSION_REQUIRED', solicita confirmación e instala con 'install_python_package'."
    ),
    tools=[connect_to_universal_source, execute_read_only_query, install_python_package]
)
