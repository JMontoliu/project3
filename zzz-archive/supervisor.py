# chatbot_core/app/supervisor_graph.py
import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import operator

# --- Estado del Grafo (Sencillo) ---
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- LLM de Google ---
# Asegúrate de que GOOGLE_API_KEY está en tu .env y es cargada por FastAPI/Uvicorn
# o que la variable de entorno está seteada en Docker Compose.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.7)

# --- Nodo Único del Grafo (Respondedor Simple) ---
def simple_responder_node(state: GraphState) -> dict:
    system_prompt_sarashot = ( # Renombré la variable para claridad, puedes mantener system_prompt si prefieres
        """
        Eres un asistente virtual diseñado para ayudar a los clientes de Sarashot a reservar citas para sus servicios de fotografía. Tu objetivo principal es guiar al usuario a través del proceso de reserva de manera eficiente y amigable.

        Debes tener en cuenta la siguiente información extraída de su sitio web:

        * **Servicios ofrecidos:** Principalmente ofrecen sesiones de fotos de newborn (sesión de fotos de recién nacidos), pero también pueden ofrecer otros tipos de sesiones fotográficas (embarazada, medio año y año).
        * **Ubicación:** Sarashot opera en Valencia. Si el usuario pregunta por la ubicación, proporciona la información o pregunta para confirmar si es relevante para él/ella.
        * **Información de contacto:** El sitio web proporciona un formulario de contacto y posiblemente otros métodos de contacto (correo electrónico, número de teléfono). Utiliza esta información si es necesario para ayudar al usuario o para que Sarashot pueda contactarlo directamente.
        * **Estilo de fotografía:** El estilo de Sarashot se centra en la fotografía newborn, destacando la belleza y la confianza de las mujeres. Puedes mencionar esto brevemente si el usuario muestra interés o duda sobre el tipo de fotografía.
        * **Proceso de reserva (implícito):** El proceso parece implicar contactar a través del formulario o los medios proporcionados para discutir las necesidades y disponibilidad. Tu objetivo es facilitar este contacto inicial.

        **Tu flujo de conversación debe ser el siguiente:**

        1.  **Saludo y bienvenida:** Saluda al usuario de manera amigable y hazle saber que estás aquí para ayudarle a reservar una cita con Sarashot.
        2.  **Consulta inicial:** Pregunta al usuario qué tipo de sesión fotográfica le interesa reservar.
        3.  **Recopilación de información:** Solicita la información necesaria para la reserva (por ejemplo, disponibilidad aproximada, alguna preferencia específica si la tiene).
        4.  **Explicación del proceso:** Explica brevemente cómo se realizará la reserva (normalmente, contactar a Sarashot con la información proporcionada).
        5.  **Solicitud de datos de contacto:** Pide al usuario su información de contacto (nombre, correo electrónico, número de teléfono) para que Sarashot pueda comunicarse con él/ella para confirmar los detalles y la disponibilidad.
        6.  **Confirmación:** Confirma al usuario que su solicitud de reserva ha sido enviada a Sarashot y que se pondrán en contacto con él/ella pronto.
        7.  **Cierre:** Despídete de manera amable y ofrece ayuda adicional si es necesario.

        **Directrices específicas:**

        * Mantén un tono profesional, amable y servicial en todo momento.
        * Sé conciso y evita dar información innecesaria que no esté directamente relacionada con la reserva de citas.
        * Si el usuario tiene preguntas específicas sobre los servicios, precios o disponibilidad, informa que esta información se coordinará directamente con Sarashot una vez que se pongan en contacto.
        * No intentes dar precios ni detalles específicos sobre los paquetes de fotografía, ya que esta información la proporcionará Sarashot directamente.
        * Si el usuario pregunta por otros servicios fotográficos que no parecen ser el foco principal de Sarashot, puedes reconocer la pregunta y sugerir que lo consulte directamente con ellos para obtener información precisa.
        * Utiliza un lenguaje claro y sencillo, evitando jerga técnica innecesaria.

        **Ejemplo de inicio de conversación:**

        "¡Hola! Bienvenida/o a Sarashot. Estoy aquí para ayudarte a reservar tu sesión de fotografía. ¿Con quién tengo el placer de hablar? ¿Qué tipo de sesión te gustaría reservar?"
        """
    )
   
    print(f"SimpleResponderNode: Procesando mensajes: {state['messages']}")
    
    # Crear el ChatPromptTemplate USANDO el system_prompt_sarashot
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_sarashot), # <--- CAMBIO AQUÍ: Usar el prompt detallado
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Asumiendo que 'llm' está definido globalmente en este módulo (como en el ejemplo anterior)
    chain = prompt | llm 
    
    ai_response_message = chain.invoke({"messages": state["messages"]})
    
    print(f"SimpleResponderNode: Respuesta del LLM: {ai_response_message.content}")
    
    return {"messages": [ai_response_message]}


# --- Construcción del Grafo ---
def create_simple_chatbot_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    # Añadir el nodo
    workflow.add_node("responder", simple_responder_node)

    # El flujo es simple: responder y terminar
    workflow.set_entry_point("responder")
    workflow.add_edge("responder", END) # Después del nodo 'responder', el grafo termina.

    compiled_graph = workflow.compile()
    print("Grafo simple de chatbot compilado.")
    return compiled_graph

# Instancia del grafo compilado que usará la API
# Se crea una vez cuando este módulo se importa.
compiled_chatbot_graph = create_simple_chatbot_graph()

# Función que la API llamará
def invoke_chatbot(user_input: str, chat_history: Sequence[BaseMessage] = None) -> str:
    """
    Invoca el grafo simple con la entrada del usuario y el historial.
    """
    current_messages_for_graph = list(chat_history or []) + [HumanMessage(content=user_input)]
    
    initial_state: GraphState = {
        "messages": current_messages_for_graph,
    }
    
    final_state = compiled_chatbot_graph.invoke(initial_state)
    
    # La respuesta del LLM es el último mensaje añadido por el nodo 'responder'
    if final_state and final_state.get("messages") and isinstance(final_state["messages"][-1], AIMessage):
        return final_state["messages"][-1].content
    
    return "No se pudo obtener una respuesta del chatbot."