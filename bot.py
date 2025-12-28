import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from orchestrator import get_reply_user

# Load credentials
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers the /start command."""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلام {user_name} عزیز! 😊\n"
        "من دستیار هوشمند دانشجویی هستم که توسط محمدحسین تاجیک طراحی شده‌ام.\n"
        "هر سوال درسی یا برنامه‌نویسی داری از من بپرس."
    )
    await update.message.reply_text(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages from users."""
    user_message = update.message.text
    
    # Show "typing..." status in Telegram while AI generates the answer
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get reply from our AI orchestrator
    ai_response = get_reply_user(user_message)
    
    # Send the response back to user
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file!")
    else:
        # Create the application
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        
        print("Bot is starting... Press Ctrl+C to stop.")
        # Start the bot
        application.run_polling()