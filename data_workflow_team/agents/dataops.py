from google.adk.agents import Agent
from data_workflow_team.integrations.git_manager import git_merge_pr, git_create_pull_request
from data_workflow_team.integrations.data_connectors import (
    install_python_package,
    connect_to_universal_source,
    execute_read_only_query,
    databricks_pipeline_operations
)
from data_workflow_team.integrations.notification_manager import send_alert_notification

def monitor_performance(pipeline_name: str) -> str:
    return f"Monitoreo de sistema SRE para '{pipeline_name}': Consumo de recursos nominal. Disponibilidad 99.9%."

def suggest_infrastructure_improvements(bottlenecks: str) -> str:
    return f"Recomendación de infraestructura: Optimizar autoscaling y almacenamiento Delta Lake para resolver '{bottlenecks}'."

dataops_agent = Agent(
    name="DataOps",
    model="gemini-2.5-flash",
    description=(
        "Ingeniero SRE, DataOps y Guardián del Ciclo de Vida, Producción y Alertas. "
        "Especializado en GITOPS GATEKEEPING Y LIBERACIONES A PRODUCCIÓN: Revisa los Pull Requests creados por el Engineer, "
        "valida que se hayan ejecutado los tests de QA, aprueba la fusión a la rama main ('git_merge_pr' en GitHub) "
        "y dispara la alerta multicanal de liberación a producción a maximilianonaranjo@gmail.com."
    ),
    instruction=(
        "Eres el DataOps/SRE del equipo, responsable de la estabilidad, gobernanza, despliegues productivos y alertas.\n\n"
        "RESPONSABILIDADES Y REGLAS GITOPS:\n"
        "1. GATEKEEPER DE PULL REQUESTS: Revisa los Pull Requests creados por el Engineer en GitHub.\n"
        "2. FUSIÓN A PRODUCCIÓN: Eres el único agente con autoridad para aprobar y fusionar Pull Requests a la rama main en GitHub mediante 'git_merge_pr(pr_number)'.\n"
        "3. DESPACHO DE ALERTA DE LIBERACIÓN: Dispara la alerta de producción mediante 'send_alert_notification' notificando la fusión a main a maximilianonaranjo@gmail.com, Slack o Teams.\n"
        "4. MONITOREO Y PIPELINES: Activa e inspecciona la ejecución de pipelines en producción mediante 'databricks_pipeline_operations' y 'monitor_performance'."
    ),
    tools=[
        monitor_performance,
        suggest_infrastructure_improvements,
        connect_to_universal_source,
        execute_read_only_query,
        databricks_pipeline_operations,
        git_merge_pr,
        git_create_pull_request,
        install_python_package,
        send_alert_notification
    ]
)
