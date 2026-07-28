import os
from google import genai
from google.genai import types
from typing import List, Callable, Any

class BaseAgent:
    """
    Clase base para todos los agentes del Data Workflow Team.
    Envuelve la interacción con el cliente de google-genai, maneja el estado
    de la conversación y enlaza las herramientas (function calling).
    """
    def __init__(self, name: str, role: str, system_instruction: str, tools: List[Callable] = None, model: str = None):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.tools = tools or []
        
        from data_workflow_team.config.settings import DEFAULT_MODEL
        self.model = model or DEFAULT_MODEL
        
        # Inicializar el cliente (requiere GEMINI_API_KEY en variables de entorno)
        # Si no se encuentra, google-genai intentará usar las credenciales por defecto de Google Cloud.
        try:
            self.client = genai.Client()
        except Exception as e:
            print(f"Advertencia: No se pudo inicializar genai.Client ({e}). Asegúrate de tener configurado GEMINI_API_KEY.")
            self.client = None
            
        # Construir la configuración. Pasamos las herramientas (funciones de Python)
        # El SDK moderno google-genai infiere automáticamente el esquema desde los type hints y docstrings.
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=self.tools if self.tools else None,
            temperature=0.2, # Baja temperatura para tareas técnicas y analíticas
        )
        
        if self.client:
            # Inicializamos una sesión de chat para mantener el contexto
            self.chat = self.client.chats.create(model=self.model, config=self.config)

    def send_message(self, message: str) -> str:
        """
        Envía un mensaje al agente. La sesión de chat interna de google-genai 
        se encarga de procesar las llamadas a herramientas automáticamente
        y devolver la respuesta final en texto.
        """
        if not self.client:
            return f"[{self.name} (Offline Mock)] Recibí el mensaje, pero el cliente genai no está configurado."
            
        try:
            # El método send_message en chats.create ya maneja el loop de function calling
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"Error interno en agente {self.name}: {str(e)}"
