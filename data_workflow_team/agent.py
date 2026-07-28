import sys
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from google.adk.agents import Agent
from data_workflow_team.config.settings import settings
from data_workflow_team.integrations.data_connectors import health_check_system
from data_workflow_team.agents.analyst import analyst_agent
from data_workflow_team.agents.explorer import explorer_agent
from data_workflow_team.agents.engineer import engineer_agent
from data_workflow_team.agents.qa import qa_agent
from data_workflow_team.agents.bi import bi_agent
from data_workflow_team.agents.dataops import dataops_agent

def _get_system_context() -> str:
    connections = []
    if settings.DATABRICKS_HOST:
        connections.append(f"  - Databricks SDK & SQL (Host: {settings.DATABRICKS_HOST}) [CONECTADO EN .ENV]")
    if settings.GITHUB_TOKEN:
        connections.append(f"  - GitHub Repository ({settings.GITHUB_REPOSITORY or 'Configurado'}) [AUTENTICADO EN .ENV]")
    if settings.TRELLO_API_KEY:
        connections.append(f"  - Trello Kanban Board (Board ID: {settings.TRELLO_BOARD_ID or 'Configurado'}) [CONECTADO EN .ENV]")
    
    if not connections:
        return "  - Ninguna credencial remota detectada en .env."
    return "\n".join(connections)

root_agent = Agent(
    name="Orchestrator",
    model="gemini-2.5-pro",
    description="Supervisor Inteligente y Enrutador Principal del Enterprise Data Workflow Team.",
    instruction=(
        "Eres el Agente Orquestador (Supervisor) Inteligente del 'Data Workflow Team'.\n"
        "Tu función principal es EVALUAR CADA SOLICITUD DEL USUARIO Y GARANTIZAR EL CICLO COMPLETO DE INGENIERÍA DE DATOS Y GITOPS:\n\n"
        "SERVICIOS Y CONEXIONES EMPRESARIALES EN EL ENTORNO:\n"
        f"{_get_system_context()}\n\n"
        "CICLO COMPLETO DE DESARROLLO DE DATOS Y GITOPS (MEJORES PRÁCTICAS):\n"
        "1. ANALYST: Crea la historia de usuario / ticket en Kanban/Trello con criterios de aceptación.\n"
        "2. ENGINEER (GitOps & IaC): Crea una rama Git ('feature/...'), guarda el código/SQL del artefacto en el repositorio ('models/'), aplica el cambio en Databricks, realiza commit/push y abre el Pull Request en GitHub.\n"
        "3. QA: Ejecuta pruebas automatizadas de calidad, valida datos/PII y aprueba el pase a QA Pass.\n"
        "4. DATAOPS (Despliegue & Gatekeeping): Revisa el Pull Request en GitHub y lo fusiona a la rama main con 'git_merge_pr'.\n"
        "5. BI: Consulta el objeto creado en main y diseña los tableros analíticos (Lakeview/PowerBI).\n\n"
        "MATRIZ RÍGIDA DE SELECCIÓN Y ENRUTAMIENTO:\n"
        "- Para crear o modificar tablas/vistas/pipelines/archivos: Delega SIEMPRE al 'Engineer' (quien iniciará el ciclo GitOps con rama y PR).\n"
        "- Para lectura/exploración de tablas existentes: Delega al 'Explorer'.\n"
        "- Para auditoría y tests de código: Delega al 'QA'.\n"
        "- Para fusionar a producción (PR merge): Delega al 'DataOps'.\n"
        "- Para dashboards: Delega al 'BI'.\n"
        "- Para diagnóstico de salud: Ejecuta 'health_check_system'."
    ),
    tools=[health_check_system],
    sub_agents=[
        analyst_agent,
        explorer_agent,
        engineer_agent,
        qa_agent,
        bi_agent,
        dataops_agent
    ]
)
