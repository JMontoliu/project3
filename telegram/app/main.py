# telegram/app/main.py
import os
import requests 
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv() # Carga .env desde la raíz del proyecto si ejecutas localmente,
              # o desde la raíz del WORKDIR si se copia en Docker.
              # Para docker-compose, las variables de .env ya están inyectadas.

TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_KEY")
CHATBOT_CORE_URL = "http://chatbot_core:8000/chat" # <--- URL DEL SERVICIO CHATBOT_CORE

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy tu bot de Telegram. Envíame un mensaje y hablaré con el Chatbot Core."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id) # Asegúrate que es string para el JSON
    user_input = update.message.text
    bot_response_text = "Lo siento, no pude contactar al chatbot." # Respuesta por defecto

    payload = {
        "thread_id": user_id,
        "message": user_input
    }

    print(f"Telegram Gateway: Enviando a Chatbot Core: {payload}")

    try:
        response = requests.post(CHATBOT_CORE_URL, json=payload, timeout=10) # timeout de 10s
        response.raise_for_status() # Lanza una excepción para errores HTTP 4xx/5xx
        
        response_data = response.json()
        bot_response_text = response_data.get("response", "No se recibió respuesta del chatbot.")
        print(f"Telegram Gateway: Recibido de Chatbot Core: {bot_response_text}")

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Chatbot Core: {e}")
        bot_response_text = "Hubo un problema de comunicación con el servicio de chat. Inténtalo más tarde."
    except Exception as e:
        print(f"Error inesperado: {e}")
        bot_response_text = "Ocurrió un error inesperado."


    await update.message.reply_text(bot_response_text)

def main() -> None:
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_API_KEY no encontrada.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot de Telegram (Gateway) iniciado y listo para hablar con Chatbot Core...")
    application.run_polling()

if __name__ == '__main__':
    main()