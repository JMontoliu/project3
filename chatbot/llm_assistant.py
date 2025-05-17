import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from assistant_tools import registrar_cita

class ChatAgentFactory:
    """Creates and holds a shared agent with its graph."""

    def __init__(self):
        # Initialize the LLM with Google Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )

        # Define available tools
        self.tools = [registrar_cita]

        # Create prompt template for the agent
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente virtual para una Fotógrafa de Embarazo y Newborn."),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])

        # Create the tool-calling agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        # Build the LangGraph state graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Builds and compiles the agent's runnable graph."""

        def run_agent(state):
            input = state["input"]
            history = state.get("chat_history", [])
            
            # Add empty intermediate_steps if not present
            agent_input = {
                "input": input, 
                "chat_history": history,
                "intermediate_steps": []  # Add this line to fix the KeyError
            }
            
            response = self.agent.invoke(agent_input)
            history.append(HumanMessage(content=input))
            
            # Handle AgentFinish object properly
            if hasattr(response, 'return_values') and 'output' in response.return_values:
                # This is an AgentFinish object
                output = response.return_values['output']
                history.append(HumanMessage(content=output))  # Add the output as a message from the assistant
                return {"output": output, "chat_history": history}
            elif hasattr(response, 'content'):
                # This is a chat message with content
                history.append(response)
                return {"output": response.content, "chat_history": history}
            else:
                # Fallback for other response types
                output = str(response)
                history.append(HumanMessage(content=output))
                return {"output": output, "chat_history": history}

        builder = StateGraph(dict)
        builder.add_node("agent", RunnableLambda(run_agent))
        builder.set_entry_point("agent")
        builder.add_edge("agent", END)
        return builder.compile()


class ChatSession:
    """Manages chat history and invokes the shared graph for a user session."""

    def __init__(self, factory: ChatAgentFactory):
        self.factory = factory
        self.chat_history = []

    def invoke(self, user_input: str) -> str:
        """Invokes the graph with current input and updates history."""
        state = {
            "input": user_input,
            "chat_history": self.chat_history
        }
        result = self.factory.graph.invoke(state)
        self.chat_history = result["chat_history"]
        return result["output"]
