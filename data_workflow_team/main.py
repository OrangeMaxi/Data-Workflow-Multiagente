import sys
import os

# Asegurar que el directorio raíz del proyecto (donde está data_workflow_team) esté en sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from data_workflow_team.core.orchestrator import Orchestrator
from data_workflow_team.agents.analyst import Analyst
from data_workflow_team.agents.explorer import Explorer
from data_workflow_team.agents.engineer import Engineer
from data_workflow_team.agents.qa import QA
from data_workflow_team.agents.bi import BI
from data_workflow_team.agents.dataops import DataOps

def main():
    print("\n🚀 Inicializando Enterprise Data Workflow Team...\n")
    
    # 1. Instanciar a todos los agentes especialistas con sus roles y herramientas (Git, Scrum, DB)
    team = {
        "Analyst": Analyst(),
        "Explorer": Explorer(),
        "Engineer": Engineer(),
        "QA": QA(),
        "BI": BI(),
        "DataOps": DataOps()
    }
    
    # 2. Inicializar al Orquestador Inteligente con el equipo
    orchestrator = Orchestrator(team)
    
    # 3. Requerimientos de prueba. El orquestador decidirá dinámicamente qué agentes despertar.
    # Prueba 1: Requerimiento analítico rápido (Debería enrutar solo al Explorer)
    req_1 = "¿Existe alguna tabla de 'ventas por temporada' en el data warehouse (postgresql://localhost:5432/dwh)?"
    
    # Prueba 2: Requerimiento de flujo completo (Debería detonar Kanban, Git, Desarrollo y Deploy)
    req_2 = (
        "El equipo de marketing necesita un pipeline que lea datos desde s3://bucket/ventas_raw.csv, "
        "limpie los nulos, no hardcodee las fechas, y construya un dashboard en PowerBI con sugerencias de visualización."
    )
    
    print("\n--- [ESCENARIO 1: Consulta Rápida] ---")
    orchestrator.process_request(req_1)
    
    print("\n\n--- [ESCENARIO 2: Pipeline Completo Agile/GitOps] ---")
    orchestrator.process_request(req_2)
    
    print("\n[Sistema] Flujo empresarial completado.")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n" + "="*70)
        print("[WARNING] GEMINI_API_KEY no configurada.")
        print("El sistema correrá en modo Offline Mock (sin conexión real al modelo).")
        print("Todas las validaciones estructurales de Git, Scrum y BBDD funcionarán.")
        print("="*70)
    
    main()
