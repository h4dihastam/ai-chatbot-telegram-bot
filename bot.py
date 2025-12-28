import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- تنظیمات لاگ ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- دریافت متغیرها از تنظیمات پلا ---
# طبق تصویر شما در پلا، نام متغیرها اینگونه است:
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- تنظیمات هوش مصنوعی گوگل ---
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("هشدار: کلید GEMINI_API_KEY یافت نشد!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلام {user_name} عزیز! 😊\n"
        "من دستیار هوشمند شما هستم که روی سرورهای ابری پلا اجرا می‌شوم.\n"
        "هر سوالی داری بپرس تا با هوش مصنوعی جواب بدم."
    )
    await update.message.reply_text(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # نمایش وضعیت تایپینگ
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        if not GEMINI_KEY:
            await update.message.reply_text("خطا: کلید هوش مصنوعی تنظیم نشده است.")
            return

        # ارسال پیام به جمینای و دریافت پاسخ
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
        
    except Exception as e:
        error_msg = f"متاسفانه مشکلی پیش آمد: {e}"
        print(error_msg)
        await update.message.reply_text("در حال حاضر امکان پاسخگویی ندارم. لطفاً بعداً تلاش کنید.")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
    else:
        # ساخت اپلیکیشن
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # افزودن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        
        print("Bot is running on Pella...")
        # اجرای ربات (حالت Polling برای پلا عالی است)
        application.run_polling()