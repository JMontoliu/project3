# chatbot_core/app/agents/calendar_agent.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage # AIMessage para el historial
from typing import Sequence, List

from .tools.assistant_tools import (
    registrar_cita, 
    modificar_reserva, 
    consultar_horarios_disponibles, 
    cancelar_reserva, 
    confirmar_reserva
)

# Lista de las herramientas específicas para este agente de calendario
calendar_tools_list = [
    registrar_cita,
    modificar_reserva,
    consultar_horarios_disponibles,
    cancelar_reserva,
    confirmar_reserva
]

# Configuración del LLM para este agente
# GOOGLE_API_KEY debe estar configurada como variable de entorno.
try:
    calendar_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", # O el modelo Gemini que prefieras
        # Puedes ajustar la temperatura; para tareas con herramientas, a veces se prefiere más baja (ej. 0.0 - 0.2)
        # para que sea más determinista al elegir herramientas y argumentos.
        temperature=0.1
    )

except Exception as e:
    print(f"CRITICAL ERROR: No se pudo inicializar ChatGoogleGenerativeAI para CalendarAgent: {e}")
    calendar_llm = None

class CalendarAgentHandler:
    def __init__(self):
        if calendar_llm is None:
            raise RuntimeError("LLM para CalendarAgent no pudo ser inicializado. Verifica la API Key y la configuración.")

        # Prompt específico para el Agente de Calendario
        # Le dice al LLM cómo debe comportarse y que tiene herramientas disponibles.
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Eres un especialista en gestión de calendarios altamente eficiente. Tu única tarea es ayudar al usuario con "
             "solicitudes relacionadas con la programación de citas utilizando EXCLUSIVAMENTE las herramientas proporcionadas. "
             "Las herramientas disponibles son: registrar_cita, modificar_reserva, consultar_horarios_disponibles, "
             "cancelar_reserva, y confirmar_reserva. "
             "Analiza cuidadosamente la conversación y la solicitud del usuario para determinar qué herramienta usar y con qué argumentos. "
             "Si necesitas más información del usuario para completar los argumentos de una herramienta (por ejemplo, falta el nombre, teléfono, fecha u hora), "
             "DEBES pedir esa información específica al usuario antes de intentar llamar a la herramienta. "
             "Una vez que una herramienta se haya ejecutado exitosamente o haya proporcionado la información necesaria, resume el resultado de forma clara para el usuario final. "
             "Si no puedes satisfacer la solicitud con las herramientas o si el usuario pregunta algo no relacionado con la gestión de citas, "
             "explícalo claramente y amablemente. No inventes información ni intentes responder fuera del ámbito de las herramientas."
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"), # La tarea o pregunta específica del usuario para este agente
            MessagesPlaceholder(variable_name="agent_scratchpad"), # Para el historial interno de llamadas a herramientas y sus resultados
        ])

        # Crear el agente que puede llamar a las herramientas de calendario
        # Este agente decide qué herramienta llamar y con qué argumentos.
        tool_calling_agent_runnable = create_tool_calling_agent(calendar_llm, calendar_tools_list, prompt)
        
        # Crear el ejecutor del agente
        # AgentExecutor se encarga del ciclo: LLM -> Tool -> LLM con resultado -> Respuesta
        self.agent_executor = AgentExecutor(
            agent=tool_calling_agent_runnable,
            tools=calendar_tools_list,
            verbose=True, # Muy útil para ver lo que el agente está pensando y haciendo
            handle_parsing_errors=True, # Intenta manejar errores si el LLM no formatea bien la llamada a la tool
            # max_iterations=5, # Para evitar bucles infinitos si el agente se atasca
        )

    def invoke(self, user_task_for_calendar: str, chat_history_for_agent: Sequence[BaseMessage]) -> str:
        """
        El Supervisor llama a este método con la tarea específica del calendario
        y el historial de conversación relevante.
        """
        print(f"CalendarAgentHandler: Recibida tarea del supervisor: '{user_task_for_calendar}'")
        print(f"CalendarAgentHandler: Historial para el agente: {chat_history_for_agent}")
        
        try:
            response = self.agent_executor.invoke({
                "input": user_task_for_calendar,
                "chat_history": chat_history_for_agent # El historial que el agente ve
            })
            
            # La salida del AgentExecutor suele estar en la clave 'output'
            output_message = response.get("output", "El agente de calendario no pudo procesar la solicitud.")
            print(f"CalendarAgentHandler: Respuesta final generada: '{output_message}'")
            return output_message
        except Exception as e:
            print(f"CalendarAgentHandler: Error durante la ejecución del agent_executor: {e}")
            import traceback
            traceback.print_exc()
            return "Lo siento, ha ocurrido un error interno al procesar tu solicitud de calendario."

