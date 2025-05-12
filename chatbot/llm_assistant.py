# chatbot.py

import os
import operator
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ChatAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7
        )
        self.state = {
            "messages": [SystemMessage(content="Eres un asistente virtual para una Fotografa de Embarazo y NewBorn.")]
        }
        self.app = self._build_graph()

    def _build_graph(self):
        def call_llm_node(state: AgentState):
            response = self.llm.invoke(state['messages'])
            return {"messages": [response]}

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
