from langchain import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

def create_chain():
    prompt_template = PromptTemplate(
        input_variables=["history", "new_input"],
        template="""
        Eres un asistente virtual de una peluqueria.

        Conversación previa: {history}
        Paciente: {new_input}
        Asistente:"""
    )

    memory = ConversationBufferMemory()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return LLMChain(llm=llm, prompt=prompt_template, memory=memory, verbose=False)