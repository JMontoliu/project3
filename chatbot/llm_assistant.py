from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
import textwrap


def create_chain():
    intent_prompt = PromptTemplate(
        input_variables=["history", "new_input"],
        template=textwrap.dedent("""
            Eres un asistente virtual para una peluquería.

            Historial de conversación:
            {history}

            Entrada del usuario: {new_input}
        """).strip()
    )

    memory = ConversationBufferMemory(memory_key="history", return_messages=False)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    return LLMChain(llm=llm, prompt=intent_prompt, memory=memory, verbose=False)
