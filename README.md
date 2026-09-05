# Speaking Video Bot

O'quvchilar speaking videolarini yuboradi, bot ularni ro'yxatdan o'tkazadi,
har bir videoni sizning shaxsiy chatingizga (o'quvchi ismi va guruhi bilan)
forward qiladi, va kunlik/haftalik hisobot beradi — kim yubordi, kim yubormadi.

## 1. Bot yaratish (Telegramda)

1. Telegramda **@BotFather** ga yozing
2. `/newbot` yuboring, so'ralganda bot nomini va username'ini kiriting (username `bot` bilan tugashi kerak)
3. Sizga token beriladi, masalan: `7123456789:AAH...` — buni saqlab qo'ying

## 2. O'zingizning chat ID raqamingizni topish

Bot videolarni SIZGA forward qilishi uchun sizning shaxsiy chat ID raqamingiz kerak:

1. Telegramda **@userinfobot** ga yozing (yoki botni ishga tushirib, o'zingiz `/start` bosing va terminal logida `update.effective_user.id` ni ko'ring)
2. Chiqqan raqamni (masalan `123456789`) saqlab qo'ying

## 3. O'rnatish

```bash
cd speaking_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env.example` faylini `.env` deb nomlang va ichiga o'z token va chat ID raqamingizni yozing:

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:
```
BOT_TOKEN=sizning_tokeningiz
TEACHER_CHAT_ID=sizning_chat_id_raqamingiz
```

## 4. Ishga tushirish

```bash
python bot.py
```

Terminalda "Bot ishga tushdi..." degan xabarni ko'rsangiz — bot ishlayapti.
Buni to'xtatmasdan ishlab turishi uchun 24/7 serverga (Railway, Render, yoki VPS) joylashtirish kerak bo'ladi — buni alohida so'rasangiz, shu bo'yicha ham yordam beraman.

## 5. Bot qanday ishlaydi

**O'quvchi tomonidan:**
- `/start` — ro'yxatdan o'tish (ism, familiya va guruh so'raladi)
- Video yoki video-xabar (kruglyashka) yuborsa — avtomatik sizga yetkaziladi

**Siz (o'qituvchi) tomonidan, botga yozib:**
- `/today` — bugungi kim video yuborgani, kim yubormaganini ko'rsatadi
- `/week` — oxirgi 7 kunlik hisobot
- `/students` — ro'yxatdan o'tgan barcha o'quvchilar ro'yxati

**Avtomatik:**
- Bot har kuni soat 21:00 da (config.py da o'zgartirish mumkin) kunlik hisobotni sizga o'zi yuboradi
- Har yakshanba kuni haftalik hisobotni ham avtomatik yuboradi

## 6. Sozlamalarni o'zgartirish

`config.py` faylida quyidagilarni o'zgartirishingiz mumkin:
- `DAILY_REPORT_HOUR` / `DAILY_REPORT_MINUTE` — kunlik hisobot qaysi soatda kelishi
- `WEEKLY_REPORT_WEEKDAY` — haftalik hisobot qaysi kunda kelishi (0=Dushanba ... 6=Yakshanba)

## 7. Fayllar tuzilishi

```
speaking_bot/
├── bot.py            # Asosiy bot logikasi
├── database.py       # Ma'lumotlar bazasi (SQLite) bilan ishlash
├── config.py         # Sozlamalar
├── requirements.txt  # Kerakli kutubxonalar
├── .env.example      # Token va chat ID uchun shablon
└── speaking_bot.db   # Bot ishga tushgach avtomatik yaratiladi (o'quvchilar va videolar bazasi)
```
