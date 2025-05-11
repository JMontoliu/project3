import os
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from langchain.memory import ConversationBufferMemory
from llm_assistant import create_chain

# Diccionario para guardar memoria por usuario
user_chains = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy un asistente virtual para reservar. ¿Cómo te puedo ayudar?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Si no existe, crear nueva memoria y cadena para ese usuario
    if user_id not in user_chains:
        memory = ConversationBufferMemory(memory_key="history", return_messages=False)
        user_chains[user_id] = create_chain()

    chain = user_chains[user_id]
    user_input = update.message.text
    
    # Obtener la intención
    intent_response = chain.invoke({"new_input": user_input})
    intent = intent_response["text"].strip().lower()

    if "reservar" in intent:
        await update.message.reply_text("¡Entendido! Vamos a reservar tu cita.")
        # Lógica para reservar (pedir fecha, etc.)
    elif "consultar horarios" in intent:
        await update.message.reply_text("Nuestro horario es de 10:00 a 20:00, de lunes a viernes.")
    elif "consultar servicios" in intent:
        await update.message.reply_text("Ofrecemos servicios de corte, coloración y tratamientos capilares.")
    elif "cancelar cita" in intent:
        await update.message.reply_text("Claro, ¿qué cita deseas cancelar? Por favor, proporciona la fecha.")
        # Lógica de cancelación
    else:
        await update.message.reply_text("Lo siento, no te he entendido. ¿Cómo puedo ayudarte?")


def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()

