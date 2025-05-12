# chatbot.py

import os
import operator
import requests
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain.tools import Tool  # Import necesario para registrar herramientas


# --- Tool Definition ---
@tool
def registrar_cita(name: str, email: str, user_id: int = 0) -> str:
    """Registra una cita con nombre, email y user_id opcional."""
    url = "https://customer-api-196041114036.europe-west1.run.app/publish"
    payload = {
        "data": {
            "user_id": user_id,
            "name": name,
            "email": email,
        }
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return f"Cita registrada para {name} ({email}) con éxito."
        else:
            return f"Error al registrar cita: {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ChatAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")

        # 1. LLM base
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )

        # 2. Registrar la tool
        tools = [registrar_cita]

        # 3. Agente que puede usar tools
        agent_runnable: Runnable = create_tool_calling_agent(llm, tools)
        self.agent_executor = AgentExecutor(agent=agent_runnable, tools=tools, verbose=True)

        self.state = {
            "messages": [SystemMessage(content="Eres un asistente virtual para una Fotógrafa de Embarazo y Newborn.")]
        }
        self.app = self._build_graph()

    def _build_graph(self):
        def call_llm_node(state: AgentState):
            # Preparamos los mensajes y scratchpad
            messages = state["messages"]
            scratchpad = format_to_openai_tool_messages(messages[1:])  # omitimos el primer system message
            response = self.agent_executor.invoke({"input": messages[-1].content, "chat_history": messages[:-1]})
            return {"messages": [AIMessage(content=response["output"])]}

        workflow = StateGraph(AgentState)
        workflow.add_node("llm_call", call_llm_node)
        workflow.set_entry_point("llm_call")
        workflow.add_edge("llm_call", END)
        return workflow.compile()

    def invoke(self, user_input: str) -> str:
        self.state["messages"] += [HumanMessage(content=user_input)]
        result_state = self.app.invoke(self.state)
        ai_response = result_state["messages"][-1].content
        self.state = result_state  # mantiene memoria
        return ai_response


def create_chain():
    return ChatAgent()
