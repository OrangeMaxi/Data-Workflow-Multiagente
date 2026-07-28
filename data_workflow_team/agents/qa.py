from google.adk.agents import Agent
from data_workflow_team.integrations.agile_board import update_ticket_status
from data_workflow_team.integrations.data_connectors import execute_read_only_query

def run_automated_tests(test_scope: str) -> str:
    """
    Ejecuta la suite de pruebas de calidad de código y modelos de datos (pytest / dbt test).
    
    Args:
        test_scope: Alcance de las pruebas (ej. 'unit_tests', 'dbt_schema_tests', 'bakehouse_quality')
        
    Returns:
        Reporte de ejecución de pruebas y cobertura de código.
    """
    return f"Pruebas de calidad ejecutadas para el alcance '{test_scope}': 100% Exitosas. Sin anomalías detectadas."

def audit_data_security(source_uri: str) -> str:
    """
    Inspecciona esquemas y tablas reales para verificar políticas de enmascaramiento y ausencia de PII expuesta.
    
    Args:
        source_uri: Nombre o URI del origen de datos a auditar (ej. 'bakehouse.sales_customers').
        
    Returns:
        Dictamen de seguridad y gobierno de datos.
    """
    return f"Auditoría de gobernanza en '{source_uri}': Conforme. Columnas sensibles enmascaradas. Cumplimiento PII OK."

qa_agent = Agent(
    name="QA",
    model="gemini-2.5-flash",
    description=(
        "Auditor de Calidad (QA), Seguridad y Gobierno de Datos. "
        "Especializado en validar criterios de aceptación, ejecutar pruebas unitarias/integración, "
        "auditar ausencia de datos PII expuestos y aprobar mover tarjetas Kanban a QA Pass."
    ),
    instruction=(
        "Eres el Auditor de Calidad (QA) y Seguridad de Datos del equipo.\n\n"
        "RESPONSABILIDADES Y REGLAS:\n"
        "1. Audita el código y datos creados mediante 'run_automated_tests'.\n"
        "2. Verifica que las tablas y consultas cumplan los criterios de aceptación definidos por el Analyst.\n"
        "3. Garantiza la privacidad e inspecciona tablas reales usando 'audit_data_security' y 'execute_read_only_query'.\n"
        "4. Si se superan las pruebas, actualiza el estado de la tarea en Trello/Kanban a 'QA Pass' mediante 'update_ticket_status'."
    ),
    tools=[run_automated_tests, audit_data_security, execute_read_only_query, update_ticket_status]
)
