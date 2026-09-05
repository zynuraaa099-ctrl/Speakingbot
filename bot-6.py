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
from datetime import time as dtime, timedelta

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

# O'quvchiga video muvaffaqiyatli qabul qilinganda navbat bilan yuboriladigan
# rag'batlantiruvchi xabarlar. Har safar ro'yxatdagi keyingi xabar yuboriladi,
# shunday qilib har safar boshqacha bo'ladi.
PRAISE_MESSAGES = [
    "🌟 Ajoyib ish! Har bir video sizni maqsadingizga bir qadam yaqinlashtiradi. Davom eting! 💪",
    "🔥 Zo'r! Bugungi mehnatingiz ertangi muvaffaqiyatingiz. Shunday davom eting! 🚀",
    "🎉 Tabriklaymiz! Sizning intilishingiz ko'rinib turibdi. C1 uzoq emas! 🏆",
    "💎 Bu safar ham vazifani bajardingiz — bu haqiqiy sabr va mehnat natijasi! 👏",
    "🌈 Har bir speaking mashqi — bu til o'rganish yo'lidagi oltin qadam. Ajoyib! ✨",
    "🚴‍♀️ Kichik qadamlar katta natijalarga olib boradi. Siz to'g'ri yo'ldasiz! 🌻",
    "🏅 Mukammal! Sizning izchilligingiz meni doim quvontiradi. Davom eting, chempion! 🥇",
    "🌞 Yana bir kun, yana bir g'alaba! Til o'rganish safaringiz ajoyib davom etmoqda 🎈",
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ro'yxatdan o'tish uchun holatlar (states)
ASK_NAME, ASK_GROUP = range(2)


# ---------- RO'YXATDAN O'TISH ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if db.is_registered(user.id):
        await update.message.reply_text(
            "Assalomu alaykum! Siz allaqachon ro'yxatdan o'tgansiz.\n"
            "Speaking videongizni shunchaki shu yerga yuboraversangiz bo'ladi."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Assalomu alaykum! Botdan foydalanish uchun avval ro'yxatdan o'tamiz.\n\n"
        "Ism va familiyangizni to'liq kiriting (masalan: Aliyev Vali):"
    )
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text("Rahmat! Endi guruhingiz nomini kiriting (masalan: B2-Evening):")
    return ASK_GROUP


async def ask_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = context.user_data["full_name"]
    group_name = update.message.text.strip()

    db.register_student(user.id, full_name, group_name, user.username)

    await update.message.reply_text(
        f"Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        f"Ism: {full_name}\n"
        f"Guruh: {group_name}\n\n"
        f"Endi speaking videongizni shu yerga yuborishingiz mumkin.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi. Qaytadan boshlash uchun /start bosing.")
    return ConversationHandler.END


# ---------- VIDEO QABUL QILISH ----------

def format_duration(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}:{secs:02d}"


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not db.is_registered(user.id):
        await update.message.reply_text(
            "Video yuborishdan oldin ro'yxatdan o'tishingiz kerak. Iltimos /start bosing."
        )
        return

    student = db.get_student(user.id)

    # Video yoki video-note (kruglyashka) davomiyligini olish.
    # Kutubxona versiyasiga qarab duration int (soniya) yoki timedelta
    # bo'lishi mumkin — ikkalasini ham to'g'ri qayta ishlaymiz.
    media = update.message.video or update.message.video_note
    raw_duration = media.duration if media else None
    if isinstance(raw_duration, timedelta):
        duration = int(raw_duration.total_seconds())
    elif raw_duration is not None:
        duration = int(raw_duration)
    else:
        duration = 0

    # 1) Darhol "qabul qilindi, tekshirilyapti" xabari
    await update.message.reply_text("📥 Video qabul qilindi. Tekshirilmoqda...")

    duration_text = format_duration(duration)
    min_duration_text = format_duration(config.MIN_VIDEO_DURATION_SECONDS)

    # 2) Davomiylikni tekshirish
    if duration < config.MIN_VIDEO_DURATION_SECONDS:
        await update.message.reply_text(
            "Videoingiz tekshirildi, afsuski davomiyligi kam bo'lgani uchun "
            "qabul qila olmayman. Boshqa jo'nating, yokida jazolanishga tayyor "
            "bo'lib keling darsga 🤨😐"
        )
        return  # Qisqa video bazaga yozilmaydi va o'qituvchiga yuborilmaydi

    # Talabga mos video — bazaga yoziladi
    db.log_submission(user.id)

    if not config.TEACHER_CHAT_ID:
        logger.warning("TEACHER_CHAT_ID sozlanmagan — video faqat bazaga yozildi, forward qilinmadi.")
        await update.message.reply_text(
            "Videoingiz tekshirildi va muvaffaqiyatli deb topildi. Bajarganingiz "
            "uchun rahmat va iloyim C1 olish nasib qilsin 🙃🙂"
        )
        return

    username_line = f"@{student['username']}" if student["username"] else "yo'q"
    caption = (
        f"🎥 Yangi speaking video\n\n"
        f"👤 Ism: {student['full_name']}\n"
        f"🏷 Guruh: {student['group_name']}\n"
        f"⏱ Davomiyligi: {duration_text}\n"
        f"🔗 Username: {username_line}"
    )

    # Xabarni to'liq (forward) shaklda o'qituvchiga yuborish
    await context.bot.forward_message(
        chat_id=config.TEACHER_CHAT_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
    )
    await context.bot.send_message(chat_id=config.TEACHER_CHAT_ID, text=caption)

    await update.message.reply_text(
        "Videoingiz tekshirildi va muvaffaqiyatli deb topildi. Bajarganingiz "
        "uchun rahmat va iloyim C1 olish nasib qilsin 🙃🙂"
    )

    # Har safar boshqacha rag'batlantiruvchi xabar yuborish
    praise_index = db.get_next_praise_index(user.id, len(PRAISE_MESSAGES))
    await update.message.reply_text(PRAISE_MESSAGES[praise_index])


# ---------- MATNLI XABARLARNI FORWARD QILISH ----------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Faqat ro'yxatdan o'tgan o'quvchilarning xabarlari forward qilinadi.
    # Ro'yxatdan o'tish jarayonidagi (ism/guruh so'rash) xabarlar bu yerga
    # kelmaydi, chunki ular ConversationHandler tomonidan avval qabul qilinadi.
    if not db.is_registered(user.id):
        return

    if not config.TEACHER_CHAT_ID:
        return

    student = db.get_student(user.id)
    username_line = f"@{student['username']}" if student["username"] else "yo'q"

    text = (
        f"💬 Yangi xabar\n\n"
        f"👤 Ism: {student['full_name']}\n"
        f"🏷 Guruh: {student['group_name']}\n"
        f"🔗 Username: {username_line}\n\n"
        f"✉️ Xabar matni:\n{update.message.text}"
    )

    await context.bot.send_message(chat_id=config.TEACHER_CHAT_ID, text=text)


# ---------- ESLATMA YUBORISH ----------

async def send_reminders_to_missing(context: ContextTypes.DEFAULT_TYPE) -> tuple[int, int]:
    """
    Bugun video yubormagan barcha ro'yxatdagi o'quvchilarga shaxsiy
    eslatma xabari yuboradi. (yuborilganlar soni, muvaffaqiyatsiz bo'lganlar soni) ni qaytaradi.
    """
    rows = db.get_missing_today(1)
    sent = 0
    failed = 0
    for row in rows:
        try:
            await context.bot.send_message(
                chat_id=row["user_id"],
                text="Siz video jo'natmadingiz, unutmang!!!!",
            )
            sent += 1
        except Exception:
            logger.warning(f"Eslatma yuborilmadi (user_id={row['user_id']})", exc_info=True)
            failed += 1
    return sent, failed


async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    sent, failed = await send_reminders_to_missing(context)
    if config.TEACHER_CHAT_ID and (sent or failed):
        await context.bot.send_message(
            chat_id=config.TEACHER_CHAT_ID,
            text=f"⏰ Avtomatik eslatma yuborildi: {sent} ta o'quvchiga yetkazildi, {failed} tasiga yetkazilmadi.",
        )


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'qituvchi istalgan vaqtda /remind buyrug'i bilan qo'lda eslatma yubora oladi."""
    await update.message.reply_text("Eslatmalar yuborilmoqda...")
    sent, failed = await send_reminders_to_missing(context)
    await update.message.reply_text(
        f"✅ Tayyor. {sent} ta o'quvchiga eslatma yetkazildi, {failed} tasiga yetkazilmadi "
        f"(ehtimol botni bloklashgan yoki hali /start bosishmagan)."
    )


# ---------- HISOBOTLAR ----------

def build_report_text(days: int, title: str) -> str:
    rows = db.get_report(days)
    if not rows:
        return f"{title}\n\nHozircha ro'yxatdan o'tgan o'quvchilar yo'q."

    lines = [title, ""]
    current_group = None
    for row in rows:
        if row["group_name"] != current_group:
            current_group = row["group_name"]
            lines.append(f"\n📚 {current_group}")
        mark = "✅" if row["cnt"] > 0 else "❌"
        lines.append(f"{mark} {row['full_name']} — {row['cnt']} ta video")
    return "\n".join(lines)


async def today_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = build_report_text(1, "📊 Bugungi hisobot")
    await update.message.reply_text(text)


async def week_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = build_report_text(7, "📊 Haftalik hisobot")
    await update.message.reply_text(text)


async def list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = db.get_all_students()
    if not students:
        await update.message.reply_text("Hozircha ro'yxatdan o'tgan o'quvchi yo'q.")
        return
    lines = ["📋 Ro'yxatdan o'tgan o'quvchilar:\n"]
    for s in students:
        lines.append(f"• {s['full_name']} ({s['group_name']})")
    await update.message.reply_text("\n".join(lines))


# ---------- AVTOMATIK HISOBOTLAR (JobQueue) ----------

async def send_daily_report_job(context: ContextTypes.DEFAULT_TYPE):
    if not config.TEACHER_CHAT_ID:
        return
    text = build_report_text(1, "📊 Kunlik hisobot (avtomatik)")
    await context.bot.send_message(chat_id=config.TEACHER_CHAT_ID, text=text)


async def send_weekly_report_job(context: ContextTypes.DEFAULT_TYPE):
    if not config.TEACHER_CHAT_ID:
        return
    text = build_report_text(7, "📊 Haftalik hisobot (avtomatik)")
    await context.bot.send_message(chat_id=config.TEACHER_CHAT_ID, text=text)


# ---------- XATOLARNI QAYD ETISH ----------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Botda xatolik yuz berdi:", exc_info=context.error)


# ---------- ISHGA TUSHIRISH ----------

def main():
    if not config.BOT_TOKEN:
        raise SystemExit("BOT_TOKEN sozlanmagan. .env faylini tekshiring.")

    db.init_db()

    app = Application.builder().token(config.BOT_TOKEN).build()

    reg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_group)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(reg_conv)
    app.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, handle_video))
    app.add_handler(CommandHandler("today", today_report))
    app.add_handler(CommandHandler("week", week_report))
    app.add_handler(CommandHandler("students", list_students))
    app.add_handler(CommandHandler("remind", remind_command))
    # Video bo'lmagan oddiy matnli xabarlarni ham o'qituvchiga yetkazish
    # (Bu eng oxirida turishi kerak — boshqa handlerlar ushlamagan matnlarni oladi)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    # Avtomatik hisobotlar
    app.job_queue.run_daily(
        send_daily_report_job,
        time=dtime(hour=config.DAILY_REPORT_HOUR, minute=config.DAILY_REPORT_MINUTE),
    )
    app.job_queue.run_daily(
        send_weekly_report_job,
        time=dtime(hour=config.DAILY_REPORT_HOUR, minute=config.DAILY_REPORT_MINUTE),
        days=(config.WEEKLY_REPORT_WEEKDAY,),
    )
    # Video yubormaganlarga haftaning belgilangan kunlarida avtomatik eslatma
    app.job_queue.run_daily(
        reminder_job,
        time=dtime(hour=config.REMINDER_HOUR, minute=config.REMINDER_MINUTE),
        days=config.REMINDER_DAYS,
    )

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
