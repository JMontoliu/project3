from langchain import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain

def create_chain(memory):
    prompt_template = PromptTemplate(
        input_variables=["history", "new_input"],
        template="""
Eres un asistente virtual de una peluquería.

Historial de conversación:
{history}

Usuario: {new_input}
Asistente:"""
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    return LLMChain(llm=llm, prompt=prompt_template, memory=memory, verbose=False)

