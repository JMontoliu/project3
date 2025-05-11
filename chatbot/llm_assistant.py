from langchain import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

def create_chain():
    intent_prompt = PromptTemplate(
        input_variables=["history", "new_input"],
        template="""
        Eres un asistente virtual para una peluquería. El objetivo es reconocer la intención del usuario en base a la conversación que ha tenido previamente.

        Historial de conversación:
        {history}

        Entrada del usuario: {new_input}

        Por favor, responde con la **intención** principal del usuario de la siguiente lista:
        - "reservar" si el usuario está buscando hacer una reserva.
        - "consultar horarios" si el usuario pregunta por los horarios de la peluquería.
        - "consultar servicios" si el usuario pregunta por los servicios disponibles.
        - "cancelar cita" si el usuario menciona que desea cancelar una cita.
        - "otros" si la intención no encaja en ninguna de las anteriores.

        Responde solo con una de las opciones anteriores (reservar, consultar horarios, consultar servicios, cancelar cita, otros).
        """
    )

    memory = ConversationBufferMemory(memory_key="history", return_messages=False)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return LLMChain(llm=llm, prompt=intent_prompt, memory=memory, verbose=False)

