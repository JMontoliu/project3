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
        user_chains[user_id] = create_chain(memory)

    chain = user_chains[user_id]
    user_input = update.message.text
    response = chain.invoke({"new_input": user_input})
    await update.message.reply_text(response["text"].strip())

def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()

