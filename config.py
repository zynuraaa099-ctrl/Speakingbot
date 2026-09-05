import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TEACHER_CHAT_ID = os.getenv("TEACHER_CHAT_ID")

if TEACHER_CHAT_ID:
    TEACHER_CHAT_ID = int(TEACHER_CHAT_ID)

# Kunlik hisobot yuboriladigan soat (24 soatlik format, bot ishlayotgan server vaqti bo'yicha)
DAILY_REPORT_HOUR = 21
DAILY_REPORT_MINUTE = 0

# Haftalik hisobot qaysi kunda yuborilsin: 0=Dushanba ... 6=Yakshanba
WEEKLY_REPORT_WEEKDAY = 6  # Yakshanba
