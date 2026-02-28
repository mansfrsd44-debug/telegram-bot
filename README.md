# Telegram Bot

## تشغيل محلي
1. ثبّت المكتبات: `pip install -r requirements.txt`
2. انسخ `.env.example` إلى `.env` وضع توكن البوت: `BOT_TOKEN=توكنك`
3. شغّل: `python sell.py`

## تشغيل 24/7 (على سيرفر)
- **Railway** / **Render** / **PythonAnywhere**: أنشئ مشروع جديد، اربط الريبو، اضبط متغير البيئة `BOT_TOKEN`، وشغّل الأمر `python sell.py`.
- **VPS (أوبونتو)**: انسخ المشروع ثم `pip install -r requirements.txt` و `export BOT_TOKEN=توكنك` واستخدم `screen` أو `systemd` لتشغيل البوت في الخلفية.
