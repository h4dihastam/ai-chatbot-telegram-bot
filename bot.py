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

# تنظیمات GapGPT
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
        # تست اتصال با ارزان‌ترین مدل
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

# بقیه کد دقیقاً مثل قبل (start, help, handle_message و ...) 
# فقط در handle_message مدل رو به grok-3-mini تغییر بده:

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (بقیه کد همان قبلی)
    try:
        response = client.chat.completions.create(
            model="grok-3-mini",  # <--- اینجا
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_message}
            ]
        )
        # ... (بقیه همون قبلی)