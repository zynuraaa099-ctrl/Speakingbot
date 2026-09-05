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

# Speaking video uchun talab qilinadigan eng kam davomiylik (soniyada)
# 120 = 2 daqiqa. Video shundan qisqa bo'lsa, bot uni rad etadi.
MIN_VIDEO_DURATION_SECONDS = 120

# Video yubormagan o'quvchilarga avtomatik eslatma yuboriladigan soat
REMINDER_HOUR = 19
REMINDER_MINUTE = 0

# Eslatma qaysi kunlari yuborilsin: 0=Dushanba, 1=Seshanba, 2=Chorshanba,
# 3=Payshanba, 4=Juma, 5=Shanba, 6=Yakshanba
# Talab bo'yicha: Seshanba, Payshanba, Shanba
REMINDER_DAYS = (1, 3, 5)
