from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# (Opcional) Si chatbot_core tuviera su propio .env
# from dotenv import load_dotenv
# load_dotenv()

app = FastAPI()

# Modelo para la entrada de la solicitud
class ChatInput(BaseModel):
    thread_id: str
    message: str

# Modelo para la salida de la respuesta
class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def handle_chat_message(chat_input: ChatInput):
    """
    Recibe un mensaje y un thread_id, y devuelve una respuesta fija por ahora.
    """
    print(f"Chatbot Core: Received message='{chat_input.message}' for thread_id='{chat_input.thread_id}'")

    # Aquí, más adelante, iría la lógica de Langchain con los agentes
    bot_reply = f"Soy Chatbot Core. Recibí: '{chat_input.message}'"

    return ChatResponse(response=bot_reply)

@app.get("/")
async def root():
    return {"message": "Chatbot Core API está funcionando!"}

if __name__ == "__main__":
    # Esto es para ejecutar localmente sin uvicorn directamente, no se usa en Docker con CMD
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)