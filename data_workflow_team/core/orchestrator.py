from data_workflow_team.core.agent_base import BaseAgent
from data_workflow_team.config.settings import ORCHESTRATOR_MODEL
from typing import Dict

class Orchestrator(BaseAgent):
    def __init__(self, team: Dict[str, BaseAgent]):
        system_prompt = (
            "Eres el Agente Orquestador (Supervisor) Inteligente del 'Data Workflow Team'.\n"
            "Tu objetivo es recibir requerimientos del usuario y decidir dinámicamente qué agentes especialistas "
            "deben intervenir. ¡No debes ejecutar un flujo secuencial rígido si no es necesario!\n\n"
            "Equipo disponible y sus roles:\n"
            + "\n".join([f"- {name}: {agent.role}" for name, agent in team.items()]) +
            "\n\nREGLAS DE ORQUESTACIÓN INTELIGENTE (ENRUTAMIENTO):\n"
            "1. Analiza el requerimiento del usuario.\n"
            "2. Decide qué agente o agentes pueden resolverlo. (Ej: Si solo preguntan si una tabla existe, envía al Explorer. "
            "Si es un pipeline completo: Analyst -> Explorer -> Engineer -> QA -> DataOps -> BI).\n"
            "3. Usa la herramienta 'delegate_task' para interactuar con los agentes especialistas uno a la vez.\n"
            "4. Cuando la tarea esté resuelta por el equipo, devuelve un reporte final al usuario resumiendo qué agentes actuaron.\n"
            "5. NO inventes soluciones de código ni reglas de negocio. Delega TODO a los especialistas."
        )
        
        self.team = team
        
        def delegate_task(agent_name: str, instructions: str) -> str:
            """
            Delega una tarea a un agente especialista del equipo y retorna su respuesta.
            
            Args:
                agent_name: Nombre exacto del agente (ej. 'Analyst', 'Explorer', 'Engineer', 'QA', 'BI', 'DataOps').
                instructions: Instrucciones explícitas con todo el contexto que el agente necesite.
            """
            if agent_name not in self.team:
                return f"Error: Agente '{agent_name}' no existe. Disponibles: {list(self.team.keys())}"
                
            print(f"\n[🚀 Orquestador -> {agent_name}]: Delegando tarea...")
            
            target_agent = self.team[agent_name]
            response = target_agent.send_message(instructions)
            
            print(f"\n[✅ {agent_name} -> Orquestador]: Tarea completada.")
            return f"Respuesta de {agent_name}:\n{response}"
            
        super().__init__(
            name="Orchestrator",
            role="Supervisor Inteligente",
            system_instruction=system_prompt,
            tools=[delegate_task],
            model=ORCHESTRATOR_MODEL
        )
        
    def process_request(self, user_prompt: str) -> str:
        """Punto de entrada principal para recibir la solicitud del usuario."""
        print("\n" + "="*50)
        print("=== [Usuario -> Orquestador] ===")
        print(user_prompt)
        print("="*50 + "\n")
        response = self.send_message(user_prompt)
        return response
