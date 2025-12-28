import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None 
SETUP_ERROR = None

if not GEMINI_API_KEY:
    SETUP_ERROR = "GEMINI_API_KEY is not set in .env file."
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # System instructions to define the AI's personality
        system_msg = """تو یک دستیار هوشمند و دلسوز دانشجویان هستی که به زبان فارسی پاسخ می‌دهی.
وظیفه اصلی تو پاسخ دادن به سوالات درسی، پروژه‌ای، برنامه‌نویسی و ارائه راهنمایی‌های تحصیلی است.

قواعد مهم:
1. پاسخ به سوالات درسی: همیشه جامع، دقیق و با لحنی محترمانه باشد.
2. سوال درباره سازنده: اگر پرسیدند چه کسی تو را ساخته، بگو:
   «من توسط محمدحسین تاجیک با استفاده از هوش مصنوعی گوگل توسعه داده شده‌ام. اینستاگرام: https://www.instagram.com/mohmels/»
"""
        
        # Using gemini-1.5-flash for faster response in Telegram
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_msg
        )
    except Exception as e:
        SETUP_ERROR = str(e)

def get_reply_user(user_text: str) -> str:
    """Processes user text and returns a response from Gemini."""
    if model is None:
        return f"⚠️ خطای سیستم: {SETUP_ERROR}"

    try:
        response = model.generate_content(user_text)
        
        # Safety check for the response
        if response.candidates and response.candidates[0].finish_reason.name == 'SAFETY':
             return "⚠️ متأسفم، به دلیل قوانین ایمنی نمی‌توانم به این سوال پاسخ دهم."
            
        return response.text.strip()
    except Exception as e:
        return f"❌ خطا در دریافت پاسخ: {str(e)}"