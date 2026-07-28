from google.adk.agents import Agent
from data_workflow_team.integrations.data_connectors import execute_read_only_query

def generate_business_insights(dataset_context: str) -> str:
    """
    Genera métricas clave (KPIs), tendencias y resúmenes ejecutivos a partir de capas curadas.
    
    Args:
        dataset_context: Nombre del dataset o tabla analítica (ej. 'bakehouse.gold_customer_kpis').
        
    Returns:
        Resumen analítico de negocio con KPIs e insights.
    """
    return f"Insights ejecutivos generados para '{dataset_context}':\n- Crecimiento mensual estimado en KPIs clave.\n- Patrones analíticos optimizados."

def generate_dashboard_spec(bi_tool: str, metrics: list) -> str:
    """
    Genera especificaciones técnicas de tableros de control para Databricks Lakeview Dashboards, Power BI o Tableau.
    
    Args:
        bi_tool: Herramienta objetivo (ej. 'Databricks Lakeview', 'PowerBI', 'Tableau')
        metrics: Lista de métricas y dimensiones a visualizar.
        
    Returns:
        Especificación técnica en formato YAML/JSON para la construcción del dashboard.
    """
    return f"Especificación de Dashboard generada para '{bi_tool}' con métricas: {metrics}."

bi_agent = Agent(
    name="BI",
    model="gemini-2.5-flash",
    description=(
        "Especialista en Business Intelligence (BI) y Visualización Analítica. "
        "Especializado en diseñar tableros de control (Databricks Lakeview Dashboards, PowerBI, Tableau), "
        "consultar capas analíticas (Gold) y sintetizar métricas de negocio para la toma de decisiones."
    ),
    instruction=(
        "Eres el Especialista BI del equipo de datos.\n\n"
        "RESPONSABILIDADES Y REGLAS:\n"
        "1. Consultar únicamente vistas y tablas curadas analíticas mediante 'execute_read_only_query'.\n"
        "2. Sintetizar insights y KPIs estratégicos usando 'generate_business_insights'.\n"
        "3. Diseñar la especificación y disposición visual de tableros para Databricks Lakeview Dashboards, Power BI o Tableau con 'generate_dashboard_spec'."
    ),
    tools=[execute_read_only_query, generate_business_insights, generate_dashboard_spec]
)
