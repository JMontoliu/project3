# main.py

import os
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from llm_assistant import create_chain  # ahora importa desde chatbot.py
from dotenv import load_dotenv

user_chains = {}
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy un asistente virtual para reservar. ¿Cómo te puedo ayudar?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in user_chains:
        user_chains[user_id] = create_chain()

    chain = user_chains[user_id]
    user_input = update.message.text
    response = chain.invoke(user_input)
    await update.message.reply_text(response.strip())

def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    application.run_polling()


if __name__ == '__main__':
    run_bot()
