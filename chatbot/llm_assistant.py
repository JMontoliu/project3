import os
import requests
from typing import TypedDict, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- Tool Definition ---
@tool
def registrar_cita(name: str, email: str, user_id: int = 0) -> str:
    """Registra una cita con nombre, email y user_id opcional."""
    url = "https://customer-api-196041114036.europe-west1.run.app/publish"
    payload = {"data": {"user_id": user_id, "name": name, "email": email}}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return f"Cita registrada para {name} ({email}) con éxito."
        else:
            return f"Error al registrar cita: {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- Clase del Agente ---
class ChatAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )

        tools = [registrar_cita]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente virtual para una Fotógrafa de Embarazo y Newborn."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=create_tool_calling_agent(llm, tools, prompt),
            tools=tools,
            verbose=True
        )

        # Historial de mensajes
        self.chat_history: Sequence[BaseMessage] = [
            SystemMessage(content="Eres un asistente virtual para una Fotógrafa de Embarazo y Newborn.")
        ]

    def invoke(self, user_input: str) -> str:
        self.chat_history.append(HumanMessage(content=user_input))
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })
        output_message = AIMessage(content=response["output"])
        self.chat_history.append(output_message)
        return output_message.content
