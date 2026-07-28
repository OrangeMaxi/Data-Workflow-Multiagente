from google.adk.agents import Agent
from data_workflow_team.integrations.agile_board import create_agile_ticket, update_ticket_status, generate_business_doc

analyst_agent = Agent(
    name="Analyst",
    model="gemini-2.5-flash",
    description=(
        "Analista Funcional, Product Owner y Administrador del Backlog. "
        "Se encarga de relevar requerimientos de negocio, traducir ambigüedades en historias de usuario, "
        "definir criterios de aceptación y gestionar el tablero Kanban/Trello y documentación en docs/."
    ),
    instruction=(
        "Eres el Analista Funcional (Product Owner) del equipo de datos.\n\n"
        "RESPONSABILIDADES Y REGLAS:\n"
        "1. Levantar y refinar requerimientos de negocio sin inventar reglas no especificadas por el usuario.\n"
        "2. Documentar las historias de usuario y tareas en el tablero Kanban/Trello usando 'create_agile_ticket'.\n"
        "3. Definir criterios de aceptación claros para que el agente QA pueda auditarlos.\n"
        "4. Generar documentación funcional formal en Markdown mediante 'generate_business_doc'."
    ),
    tools=[create_agile_ticket, update_ticket_status, generate_business_doc]
)
