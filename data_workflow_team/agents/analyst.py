from google.adk.agents import Agent
from data_workflow_team.integrations.agile_board import create_agile_ticket, update_ticket_status, generate_business_doc
from data_workflow_team.integrations.git_manager import git_create_issue

analyst_agent = Agent(
    name="Analyst",
    model="gemini-2.5-flash",
    description=(
        "Analista Funcional, Product Owner y Administrador del Backlog. "
        "Se encarga de relevar requerimientos de negocio, traducir ambigüedades en historias de usuario, "
        "crear GitHub Issues ('git_create_issue'), gestionar tarjetas en Trello/Kanban y generar documentación en docs/."
    ),
    instruction=(
        "Eres el Analista Funcional (Product Owner) del equipo de datos.\n\n"
        "RESPONSABILIDADES Y REGLAS GITOPS:\n"
        "1. Relevar requerimientos de negocio sin inventar reglas no especificadas por el usuario.\n"
        "2. GITHUB ISSUES & BACKLOG: Para cada requerimiento, crea un Issue en GitHub con 'git_create_issue' y una tarjeta en Trello con 'create_agile_ticket'.\n"
        "3. Definir criterios de aceptación claros para que el agente QA pueda auditarlos.\n"
        "4. Generar documentación funcional formal en Markdown mediante 'generate_business_doc'."
    ),
    tools=[create_agile_ticket, update_ticket_status, generate_business_doc, git_create_issue]
)
