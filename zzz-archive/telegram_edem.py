import os
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from llm_assistant import ChatAgentFactory, ChatSession

load_dotenv()

# Shared agent for all users (initialized once)
agent_factory = ChatAgentFactory()

# Stores chat sessions per user
user_sessions = {}


# Handles the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy un asistente virtual para reservar. ¿Cómo te puedo ayudar?"
    )

# Handles incoming user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # Create a new session if it's a new user
    if user_id not in user_sessions:
        user_sessions[user_id] = ChatSession(agent_factory)

    session = user_sessions[user_id]
    user_input = update.message.text
    response = session.invoke(user_input)

    await update.message.reply_text(response.strip())

# Starts the Telegram bot
def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
