# chatbot_core/app/agent_with_tools.py
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # <--- ASEGÚRATE DE TENER ESTO
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Importar las herramientas
from .tools.assistant_tools import all_assistant_tools

# --- Estado del Grafo ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# --- LLM de Google ---
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest", 
        temperature=0.5 # Temperatura moderada
    )

except Exception as e:
    print(f"CRITICAL ERROR: No se pudo inicializar LLM: {e}")
    llm = None # Cambiado a llm base
    # llm_with_tools = None


# --- Nodos del Grafo ---

def agent_llm_node(state: AgentState) -> dict:
    """Nodo que llama al LLM principal del agente (que puede decidir usar una herramienta)."""
    if llm is None: # Revisamos el llm base
        return {"messages": [AIMessage(content="Error: El modelo de lenguaje no está disponible.")]}
    
    print("Agent LLM Node: Procesando...")
    
    system_prompt_text = (
        "Eres 'GestorBot', un asistente virtual experto y amigable para 'Sarashot', una fotógrafa de newborn y embarazo en Valencia. "
        "Tu objetivo principal es ayudar a los clientes a gestionar citas y obtener información sobre servicios usando las herramientas disponibles. "
        "Las herramientas que puedes usar son: registrar_cita, modificar_reserva, consultar_horarios_disponibles, cancelar_reserva, confirmar_reserva, "
        "get_current_datetime_in_spain (para saber la fecha y hora actual en España), y get_weather_forecast (para obtener el pronóstico del tiempo, por defecto en Valencia pero puedes especificar otra ciudad y país como 'Madrid,ES').\n\n" # <--- AÑADIDAS NUEVAS HERRAMIENTAS A LA DESCRIPCIÓN
        "INSTRUCCIONES DE COMPORTAMIENTO:\n"
        "1. Saluda amablemente y pregunta cómo puedes ayudar o qué tipo de sesión le interesa (newborn, embarazada, medio año, un año).\n"
        "2. ANALIZA la solicitud del usuario y el historial de conversación.\n"
        "3. DECIDE si una de tus herramientas puede ayudar. Si es así, PREPARA los argumentos EXACTOS que necesita la herramienta basándote en la conversación. Si falta información para una herramienta, PIDE AL USUARIO esa información específica de forma clara y amigable ANTES de intentar llamar a la herramienta.\n"
        "4. LLAMA a la herramienta SOLO cuando tengas todos los argumentos necesarios para ella.\n"
        "5. DESPUÉS de que una herramienta se ejecute, o si ninguna herramienta es apropiada para la última consulta del usuario, RESPONDE al usuario de forma conversacional, clara y útil. Confirma las acciones realizadas o la información encontrada. Guía la conversación si es necesario.\n"
        "6. Si no puedes ayudar o no entiendes, pide clarificación o explica tus limitaciones amablemente.\n"
        "7. Información de Sarashot: opera en Valencia. Estilo: fotografía newborn, belleza y confianza de las mujeres. Proceso de reserva: facilitar contacto inicial, Sarashot contacta para confirmar detalles y disponibilidad."
        "No des precios ni detalles de paquetes, eso lo hará Sarashot directamente."
        "Ejemplo de inicio: '¡Hola! Bienvenida/o a Sarashot. Soy GestorBot, ¿en qué puedo ayudarte hoy? ¿Qué tipo de sesión te gustaría reservar?'"
    )

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder(variable_name="messages_history") 
    ])
    
    # Construimos la cadena: Prompt -> LLM (con herramientas vinculadas)
    if hasattr(llm, 'bind_tools'): # Comprobación por si acaso
        agent_chain = prompt | llm.bind_tools(all_assistant_tools) # Vincular herramientas aquí para esta cadena específica
    else: # Fallback si algo va mal con la instancia del llm
        print("Advertencia: LLM no tiene bind_tools, el llamado a herramientas podría no funcionar como se espera.")
        agent_chain = prompt | llm

    # El LLM devolverá un AIMessage, que puede contener `tool_calls`
    # Pasamos el historial de mensajes completo al prompt
    response_ai_message = agent_chain.invoke({"messages_history": state["messages"]}) 
    
    print(f"Agent LLM Node: Respuesta del LLM: {response_ai_message}")
    return {"messages": [response_ai_message]}


# Nodo preconstruido para ejecutar las herramientas (se mantiene igual)
tool_node = ToolNode(all_assistant_tools)


# --- Construcción del Grafo (se mantiene igual) ---
def create_agent_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("agent_llm", agent_llm_node)
    builder.add_node("tools_executor", tool_node) # Ya tienes este nodo definido

    builder.set_entry_point("agent_llm")


    builder.add_conditional_edges(
        "agent_llm",    # Nodo de origen
        tools_condition, # Función de LangGraph que revisa `tool_calls`
        # `tools_condition` devuelve la clave "tools" o "__end__"
        # Ahora proveemos el mapeo para esas claves:
        {
            "tools": "tools_executor", # Si tools_condition devuelve "tools", ir al nodo "tools_executor"
            "__end__": END             # Si tools_condition devuelve "__end__", ir al nodo final END
        }
    )
    
    # Después de que la herramienta se ejecuta, su resultado (como ToolMessage)
    # se añade al estado 'messages' por el ToolNode.
    # Volvemos al LLM para que procese ese resultado y genere la respuesta final.
    builder.add_edge("tools_executor", "agent_llm") 

    compiled_graph = builder.compile()
    print("Grafo de Agente con Herramientas (corregido) compilado.")
    return compiled_graph


# Instancia del grafo (se mantiene igual)
compiled_agent_graph = create_agent_graph()

# Función que la API llamará (se mantiene igual)
def invoke_agent_with_tools(user_input: str, chat_history: Sequence[BaseMessage] = None) -> str:
    current_messages_for_graph = list(chat_history or []) + [HumanMessage(content=user_input)]
    initial_state: AgentState = {"messages": current_messages_for_graph}
    
    final_state = compiled_agent_graph.invoke(initial_state, {"recursion_limit": 10})
    
    if final_state and final_state.get("messages") and isinstance(final_state["messages"][-1], AIMessage):
        if not (hasattr(final_state["messages"][-1], "tool_calls") and final_state["messages"][-1].tool_calls):
            return final_state["messages"][-1].content
            
    return "No se pudo obtener una respuesta clara del agente (con system prompt)."