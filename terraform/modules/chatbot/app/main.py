# chatbot_core/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List 


from .agent_with_tools import invoke_agent_with_tools, BaseMessage, HumanMessage, AIMessage

load_dotenv() 

app = FastAPI()

chat_histories_db: dict[str, List[BaseMessage]] = {}

class ChatInput(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def handle_chat_message(chat_input: ChatInput):
    thread_id = chat_input.thread_id
    user_input_message = chat_input.message

    print(f"API: Recibido mensaje='{user_input_message}' para thread_id='{thread_id}'")

    if thread_id not in chat_histories_db:
        chat_histories_db[thread_id] = []
    current_chat_history = chat_histories_db[thread_id]

    try:
        
        # Llamamos a la nueva función invoke_agent_with_tools
        ai_reply_content = invoke_agent_with_tools(
            user_input=user_input_message,
            chat_history=current_chat_history
        )
        
        # Actualizar el historial (se mantiene igual)
        current_chat_history.append(HumanMessage(content=user_input_message))
        # Es importante que ai_reply_content sea el string de la respuesta final del agente
        current_chat_history.append(AIMessage(content=ai_reply_content)) 
        
        max_history_length = 10 # 5 intercambios (humano + IA)
        if len(current_chat_history) > max_history_length:
            chat_histories_db[thread_id] = current_chat_history[-max_history_length:]

        print(f"API: Respuesta del agente='{ai_reply_content}'")
        return ChatResponse(response=ai_reply_content)

    except Exception as e:
        print(f"API Error: Excepción durante la invocación del agente: {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(response=f"Error interno del servidor: {str(e)}")

@app.get("/")
async def root():
    # Mensaje opcionalmente actualizado para reflejar el cambio
    return {"message": "Chatbot Core API con Agente Único y Herramientas está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020, reload=True)