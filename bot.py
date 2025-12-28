import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دریافت متغیرهای محیطی
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# تنظیمات Gemini
model = None
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        
        system_instruction = """تو یک دستیار هوشمند فارسی‌زبان هستی که توسط محمدحسین تاجیک ساخته شده‌ای.
وظیفه اصلی‌ات کمک به دانشجویان در زمینه‌های مختلف است:
- پاسخ به سوالات درسی و تحصیلی
- کمک در حل تمرین‌ها و پروژه‌ها
- کمک در برنامه‌نویسی
- راهنمایی تحصیلی

اگر کسی پرسید چه کسی تو را ساخته، بگو: "من توسط محمدحسین تاجیک ساخته شدم."
همیشه با لحنی دوستانه، محترمانه و حمایتی پاسخ بده."""
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_instruction
        )
        logger.info("Gemini model initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Gemini: {e}")
else:
    logger.error("GEMINI_API_KEY not found!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام خوش‌آمدگویی"""
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
    """راهنمای استفاده"""
    help_text = """📚 راهنمای استفاده:

🔹 برای استفاده از ربات، کافیست سوال یا پیام خود را بنویسید
🔹 می‌توانید از من در زمینه‌های مختلف سوال بپرسید
🔹 پاسخ‌ها با استفاده از هوش مصنوعی Gemini تولید می‌شوند

مثال‌ها:
• Python چیست؟
• یک شعر زیبا بگو
• کمکم کن یک برنامه بنویسم

سوال خود را بپرسید! 💭"""
    
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های کاربر"""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Message from {user_name}: {user_message}")
    
    # نمایش وضعیت تایپ
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    if not model:
        await update.message.reply_text(
            "❌ متأسفانه سرویس هوش مصنوعی در دسترس نیست.\n"
            "لطفاً بعداً تلاش کنید."
        )
        return
    
    try:
        # ارسال پیام به Gemini
        response = model.generate_content(user_message)
        
        # بررسی ایمنی پاسخ
        if response.candidates and response.candidates[0].finish_reason.name == 'SAFETY':
            await update.message.reply_text(
                "⚠️ متأسفم، به دلیل قوانین ایمنی نمی‌توانم به این پیام پاسخ دهم."
            )
            return
        
        # ارسال پاسخ
        reply_text = response.text.strip()
        
        # تقسیم پیام‌های بلند (حداکثر 4096 کاراکتر در تلگرام)
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
    """مدیریت خطاها"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """تابع اصلی برای اجرای ربات"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return
    
    # ساخت اپلیکیشن
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # اضافه کردن هندلر خطا
    application.add_error_handler(error_handler)
    
    # اجرای ربات
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()