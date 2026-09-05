"""
Speaking video qabul qiluvchi va kuzatuvchi Telegram bot.

Ishlash tartibi:
1. O'quvchi /start bosadi -> ism va guruhini kiritadi (ro'yxatdan o'tish)
2. O'quvchi video/video-note (kruglyashka) yuborsa -> bot uni o'qituvchining
   shaxsiy chatiga o'quvchi ismi, guruhi va vaqti bilan forward qiladi
3. Har bir yuborilgan video bazaga yoziladi -> kunlik/haftalik hisobot uchun
4. O'qituvchi /today va /week buyruqlari bilan hisobotni istalgan vaqtda ko'ra oladi
5. Bot avtomatik ravishda har kuni va har hafta hisobotni o'qituvchiga jo'natadi
"""
import logging
from datetime import time as dtime

from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import config
import database as db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
