# telegram/app/main.py
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests 
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()  # Carga .env

# 1. Puerto dinámico que Cloud Run inyecta
PORT = int(os.getenv("PORT", "8030"))

# 2. Servidor HTTP mínimo para health checks
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

# 3. Lanza el health server en background
threading.Thread(target=start_health_server, daemon=True).start()


# Variables Telegram + Chatbot Core
TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_KEY")
_base = os.getenv("URL_CHATBOT", "").rstrip("/")
CHATBOT_CORE_URL = f"{_base}/chat"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy tu bot de Telegram. Envíame un mensaje y hablaré con el Chatbot Core."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)  # Asegúrate que es string
    user_input = update.message.text
    bot_response_text = "Lo siento, no pude contactar al chatbot."

    payload = {"thread_id": user_id, "message": user_input}
    print(f"Enviando a Chatbot Core ({CHATBOT_CORE_URL}): {payload}")

    try:
        r = requests.post(CHATBOT_CORE_URL, json=payload, timeout=10)
        r.raise_for_status()
        bot_response_text = r.json().get("response", bot_response_text)
    except Exception as e:
        print(f"Error: {e}")

    await update.message.reply_text(bot_response_text)

def main() -> None:
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_API_KEY no encontrada.")
        return
    if not _base:
        print("Error: URL_CHATBOT no configurada.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Bot iniciado; health‐check en 0.0.0.0:{PORT}")
    application.run_polling()

if __name__ == '__main__':
    main()
