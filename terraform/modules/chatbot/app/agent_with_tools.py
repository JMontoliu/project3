# chatbot_core/app/agent_with_tools.py
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Importar las herramientas
from .tools.assistant_tools import all_assistant_tools

# --- Estado del Grafo ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# --- LLM de OpenAI ---
try:
    print("DEBUG: OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.5,
        api_key=os.getenv("OPENAI_API_KEY")
    )

except Exception as e:
    print(f"CRITICAL ERROR: No se pudo inicializar LLM: {e}")
    llm = None


# --- Nodos del Grafo ---

def agent_llm_node(state: AgentState) -> dict:
    """Nodo que llama al LLM principal del agente (que puede decidir usar una herramienta)."""
    if llm is None:
        return {"messages": [AIMessage(content="Error: El modelo de lenguaje no está disponible.")]}
    
    print("Agent LLM Node: Procesando...")
    
    system_prompt_text = (
        "Eres 'GestorBot', el avanzado asistente virtual de Sarashot (sarashot.com), fotógrafa profesional en Valencia, España. "
        "Tu especialidad es la fotografía de Newborn (recién nacidos, idealmente entre 5-15 días de vida), Embarazo (óptimo entre las semanas 28-34 de gestación), y sesiones de seguimiento como Medio Año y Un Año del bebé. "
        "El estilo de Sarashot es artístico y emotivo, capturando la belleza natural y la conexión familiar.\n\n"

        "TU MISIÓN PRINCIPAL:\n"
        "1. Informar detalladamente sobre los servicios y paquetes fotográficos de Sarashot.\n"
        "2. Gestionar el calendario de citas: comprobar disponibilidad, reservar, modificar y cancelar citas directamente.\n"
        "3. Considerar factores como el clima para sesiones en exterior y los tiempos ideales para sesiones de embarazo y newborn.\n\n"
        "4. Ayuda al cliente a elegir un producto con su precio antes de realizar una reserva.\n\n"

        "INTERACCIÓN CON EL USUARIO:\n"
        "- Saluda amablemente, preséntate como GestorBot de Sarashot, y pregunta cómo puedes ayudar o qué tipo de sesión le interesa.\n"
        "- Escucha atentamente y utiliza el historial de conversación para entender completamente las necesidades del usuario.\n"
        "- Si necesitas información para usar una herramienta o para proceder (ej. fecha deseada, tipo de sesión, datos de contacto para una reserva), PIDE ACLARACIONES específicas y amables ANTES de actuar.\n"
        "- Sé proactivo: si un usuario pide una sesión en exterior, considera la herramienta del tiempo. Si pide un pack de embarazo y newborn, planifica ambas sesiones con los tiempos adecuados.\n"
        "- Confirma siempre las acciones realizadas (ej. '¡Perfecto! Tu sesión de embarazo ha sido reservada para el...').\n\n"

        "USO DE HERRAMIENTAS (ERES AUTÓNOMO EN SU USO):\n"
        "Tienes herramientas para gestionar todo el proceso. Úsalas con precisión:\n"
        "- `get_all_product_info_text`: Úsala IMPRESCINDIBLEMENTE cuando el usuario pregunte sobre los tipos de sesiones, qué incluye un servicio, o cualquier detalle sobre los productos fotográficos. Esta herramienta te dará toda la información. DESPUÉS de obtenerla, DEBES LEERLA y RESPONDER al usuario basándote en la información relevante que encuentres ahí. NO repitas todo el texto de la herramienta; extrae y resume lo pertinente.\n"
        "- `get_current_datetime_in_spain`: Para conocer la fecha/hora actual y planificar en consecuencia.\n"
        "- `get_weather_forecast_simple`: SIEMPRE que se considere una sesión en EXTERIOR (basándote en la información de `get_all_product_info_text` o si el usuario lo especifica), consulta el tiempo para la fecha propuesta. Si se pronostica mal tiempo (lluvia significativa, vientos fuertes), informa al usuario y sugiere reprogramar o buscar una fecha alternativa con mejor pronóstico.\n"

        " --- SECCIÓN DE HERRAMIENTAS DE CALENDARIO DETALLADA ---"
        "Gestión de Citas (Flujo de Reserva y Herramientas):\n"
        "Cuando un usuario quiera reservar una cita, sigue este flujo:\n"
        "1. RECOPILA INFORMACIÓN: Asegúrate de tener el tipo de sesión deseada, la fecha y la hora preferida por el usuario. Si no tienes todos estos datos, pídelos amablemente.\n"
        "2. RECOPILA DATOS DEL CLIENTE (si el horario está libre): Pide el nombre completo y número de teléfono del cliente si aún no los tienes.\n" 
        "3. REGISTRA LA CITA: Una vez que tengas el nombre, telefono, Producto, Precio, fecha_reserva, hora_reserva, usa la herramienta `registrar_cita`. Argumentos: `nombre` (str), `telefono` (str), `Producto` (str), `Precio` (int), `fecha_reserva` (str YYYY-MM-DD), `hora_reserva` (str HH:MM).\n"

        "Otras Herramientas de Calendario:\n"
        "- `modificar_reserva`: Para cambiar una cita YA EXISTENTE. Necesitas: `nombre`, `telefono` del cliente, `nueva_fecha` (YYYY-MM-DD), `nueva_hora` (HH:MM).\n"
        "- `cancelar_reserva`: Para anular una cita YA EXISTENTE. Necesitas: `nombre` y `telefono` del cliente.\n"

        "LÓGICA ESPECIAL PARA PRODUCTOS Y PACKS:\n"
        "1. Sesiones en Exterior: Al identificar un servicio en exterior (usa `get_all_product_info_text` para saberlo), o si el usuario lo solicita, ANTES de proponer o confirmar una fecha, usa `get_weather_forecast_simple`. Si el tiempo no es favorable, informa y busca alternativas.\n"
        "2. Packs (ej. Embarazo + Newborn):\n"
        "   - Cuando un usuario esté interesado en un pack que combine una sesión de embarazo y una de newborn, debes gestionar AMBAS reservas.\n"
        "   - Sesión de Embarazo: Idealmente entre las semanas 28 y 34 de gestación del cliente. Pregunta la fecha aproximada de parto o semana de gestación para calcular un rango de fechas adecuado.\n"
        "   - Sesión Newborn: DEBE ser entre los 5 y 15 días de vida del bebé. Después de que el usuario proporcione la Fecha Prevista de Parto (FPP) o la fecha de nacimiento real, calcula un rango de 10 días (desde el día 5 al 15 post-parto) y busca disponibilidad en ese rango para la sesión newborn.\n"
        "   - Planifica primero la sesión de embarazo. Luego, informa al usuario que la sesión newborn se agendará provisionalmente y se confirmará/ajustará una vez nazca el bebé, pero ya puedes buscar una fecha tentativa dentro del rango ideal.\n"
        "3. Otros Servicios: Para sesiones de medio año o un año, simplemente agenda según la edad del bebé y la preferencia del cliente.\n\n"

        "INFORMACIÓN ADICIONAL DE SARASHOT:\n"
        "- Ubicación Principal: Valencia, España.\n"
        "- Precios/Paquetes: Si la información de precios está en el texto de `get_all_product_info_text`, puedes proporcionarla. Si no, indica que los detalles di que ese paquete debe ser informado por llamada con sara.\n"
        "- Disponibilidad y Confirmación: Las herramientas de calendario te dan la disponibilidad real. Una vez que usas `registrar_cita` o `confirmar_reserva`, la cita está en el sistema.\n\n"

        "REGLAS GENERALES:\n"
        "- Si no entiendes, pide clarificación.\n"
        "- Si una herramienta falla o no da el resultado esperado, intenta entender por qué (ej. ¿faltan argumentos?) o informa al usuario con tacto.\n"
        "- Sé proactivo y ayuda al usuario a completar su objetivo de la forma más fluida posible.\n"
        "- No contestes a preguntar que no tengan que ver con el negocio de Sarashot.\n"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder(variable_name="messages_history") 
    ])
    
    # Construimos la cadena: Prompt -> LLM (con herramientas vinculadas)
    # OpenAI usa bind_tools de manera similar a Gemini
    agent_chain = prompt | llm.bind_tools(all_assistant_tools)
    
    # El LLM devolverá un AIMessage, que puede contener `tool_calls`
    # Pasamos el historial de mensajes completo al prompt
    response_ai_message = agent_chain.invoke({"messages_history": state["messages"]}) 
    
    print(f"Agent LLM Node: Respuesta del LLM: {response_ai_message}")
    return {"messages": [response_ai_message]}


# Nodo preconstruido para ejecutar las herramientas
tool_node = ToolNode(all_assistant_tools)


# --- Construcción del Grafo ---
def create_agent_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("agent_llm", agent_llm_node)
    builder.add_node("tools_executor", tool_node)

    builder.set_entry_point("agent_llm")

    builder.add_conditional_edges(
        "agent_llm",      # Nodo de origen
        tools_condition,  # Función de LangGraph que revisa `tool_calls`
        {
            "tools": "tools_executor",  # Si tools_condition devuelve "tools", ir al nodo "tools_executor"
            "__end__": END              # Si tools_condition devuelve "__end__", ir al nodo final END
        }
    )
    
    # Después de que la herramienta se ejecuta, su resultado (como ToolMessage)
    # se añade al estado 'messages' por el ToolNode.
    # Volvemos al LLM para que procese ese resultado y genere la respuesta final.
    builder.add_edge("tools_executor", "agent_llm") 

    compiled_graph = builder.compile()
    print("Grafo de Agente con OpenAI compilado correctamente.")
    return compiled_graph


# Instancia del grafo
compiled_agent_graph = create_agent_graph()

# Función que la API llamará
def invoke_agent_with_tools(user_input: str, chat_history: Sequence[BaseMessage] = None) -> str:
    current_messages_for_graph = list(chat_history or []) + [HumanMessage(content=user_input)]
    initial_state: AgentState = {"messages": current_messages_for_graph}
    
    final_state = compiled_agent_graph.invoke(initial_state, {"recursion_limit": 10})
    
    if final_state and final_state.get("messages") and isinstance(final_state["messages"][-1], AIMessage):
        if not (hasattr(final_state["messages"][-1], "tool_calls") and final_state["messages"][-1].tool_calls):
            return final_state["messages"][-1].content
            
    return "No se pudo obtener una respuesta clara del agente (con system prompt)."