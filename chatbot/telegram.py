import os
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from llm_assistant import create_chain

chain = create_chain()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy un asistente virtual para reservar. ¿Como te puedo ayudar?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    response = chain.invoke({"new_input": user_input})
    await update.message.reply_text(response["text"].strip())


def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot iniciado...")
    application.run_polling()


if __name__ == '__main__':
    run_bot()
