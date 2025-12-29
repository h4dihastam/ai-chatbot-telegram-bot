import os
import logging
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from flask import Flask
from threading import Thread

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دریافت متغیرهای محیطی
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GAPGPT_API_KEY = os.getenv("GAPGPT_API_KEY")

# تنظیمات GapGPT - ارزان‌ترین مدل: grok-3-mini
client = None
system_msg = """تو یک دستیار هوشمند فارسی‌زبان هستی که توسط محمدحسین تاجیک ساخته شده‌ای.
وظیفه اصلی‌ات کمک به دانشجویان در زمینه‌های مختلف است:
- پاسخ به سوالات درسی و تحصیلی
- کمک در حل تمرین‌ها و پروژه‌ها
- کمک در برنامه‌نویسی
- راهنمایی تحصیلی

اگر کسی پرسید چه کسی تو را ساخته، بگو: "من توسط محمدحسین تاجیک ساخته شدم."
همیشه با لحنی دوستانه، محترمانه و حمایتی پاسخ بده."""

if GAPGPT_API_KEY:
    try:
        client = OpenAI(
            base_url='https://api.gapgpt.app/v1',
            api_key=GAPGPT_API_KEY,
            timeout=30.0,
            max_retries=2
        )
        # تست اتصال با مدل ارزان و موجود
        test_response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[{"role": "user", "content": "سلام"}],
            max_tokens=10
        )
        logger.info("GapGPT client initialized and tested successfully with grok-3-mini")
    except Exception as e:
        logger.error(f"Error initializing GapGPT: {e}")
        client = None
else:
    logger.error("GAPGPT_API_KEY not found!")
    client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = f"""سلام {user_name} عزیز! 👋

من توسط محمدحسین تاجیک نوشته شدم و یک دستیار هوشمند برای کمک به دانشجویان هستم.

💡 از من می‌توانید:
• درباره دروس خود سوال بپرسید
• کمک در حل تمرین‌ها و پروژه‌ها
• یادگیری برنامه‌نویسی
• راهنمایی تحصیلی

📌 دستورات موجود:
/start - شروع مجدد ربات
/help - راهنمای استفاده

سوالات درسی یا هر سوال دیگری داری بپرس! 📚✨"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 راهنمای استفاده:

🔹 برای استفاده از ربات، کافیست سوال یا پیام خود را بنویسید
🔹 پاسخ‌ها با هوش مصنوعی پیشرفته و ارزان تولید می‌شوند

مثال‌ها:
• Python چیست؟
• یک شعر زیبا بگو
• کمکم کن یک برنامه بنویسم

سوال خود را بپرسید! 💭"""
    
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Message from {user_name}: {user_message}")
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    if not client:
        await update.message.reply_text(
            "❌ متأسفانه سرویس هوش مصنوعی در دسترس نیست.\n"
            "لطفاً بعداً تلاش کنید."
        )
        return
    
    try:
        response = client.chat.completions.create(
            model="grok-3-mini",  # ارزان‌ترین و موجود
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_message}
            ]
        )
        
        reply_text = response.choices[0].message.content.strip()
        
        if len(reply_text) > 4096:
            for i in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[i:i+4096])
        else:
            await update.message.reply_text(reply_text)
        
        logger.info(f"Response sent to {user_name}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "❌ متأسفانه در پردازش پیام شما مشکلی پیش آمد.\n"
            "لطفاً دوباره تلاش کنید."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# وب‌سرور برای Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram Bot is running!", 200

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}, 200

def run_flask():
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return
    
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask thread started, waiting for server to be ready...")
    time.sleep(2)
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()