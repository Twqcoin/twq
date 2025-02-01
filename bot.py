import os
import logging
import psycopg2
import certifi
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse
import asyncio

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تعريف تطبيق Flask
app = Flask(__name__)

# إعداد اتصال بقاعدة بيانات PostgreSQL
def get_db_connection():
    """
    إنشاء اتصال بقاعدة البيانات باستخدام DATABASE_URL من المتغيرات البيئية.
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
            return None

        result = urlparse(database_url)
        logger.info(f"محاولة الاتصال بقاعدة البيانات: host={result.hostname}, db={result.path[1:]}")

        # إعداد اتصال بقاعدة البيانات
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            sslmode='require' if 'sslmode=require' in database_url else 'disable',
            sslrootcert=certifi.where() if 'sslmode=require' in database_url else None
        )
        logger.info("تم الاتصال بقاعدة البيانات بنجاح!")
        return conn
    except Exception as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {e}", exc_info=True)
        return None

# إنشاء قاعدة البيانات (إذا لم تكن موجودة)
def create_db():
    """
    إنشاء جدول players إذا لم يكن موجودًا.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن إنشاء قاعدة البيانات. لم يتم الاتصال بالخادم.")
                return

            with conn.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                                    id SERIAL PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    image_url TEXT NOT NULL,
                                    progress INTEGER DEFAULT 0,
                                    mining_progress INTEGER DEFAULT 0,
                                    tasks_completed TEXT DEFAULT '')''')
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء الجدول: {e}", exc_info=True)

# إضافة لاعب إلى قاعدة البيانات
def add_player_to_db(player_name, player_image_url):
    """
    إضافة لاعب جديد إلى قاعدة البيانات.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن إضافة اللاعب. لم يتم الاتصال بقاعدة البيانات.")
                return

            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM players WHERE name = %s", (player_name,))
                if cursor.fetchone():
                    logger.error(f"اللاعب {player_name} موجود بالفعل.")
                    return

                cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                               (player_name, player_image_url, 0))
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة اللاعب: {e}", exc_info=True)

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    بدء استخدام البوت وعرض زر "Play Game".
    """
    keyboard = [
        [InlineKeyboardButton(
            text="Play Game",
            web_app={"url": "https://twq-xzy4.onrender.com"}  # هنا يتم فتح رابط اللعبة
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "مرحبًا! اضغط على الزر أدناه للعب:",
        reply_markup=reply_markup
    )

# استلام بيانات اللاعب عند الضغط على "Play Game"
@app.route("/receive_player_data", methods=["POST"])
def receive_player_data():
    player_data = request.json
    player_name = player_data.get("name")
    player_image_url = player_data.get("image_url")
    
    if player_name and player_image_url:
        # إضافة اللاعب إلى قاعدة البيانات
        add_player_to_db(player_name, player_image_url)
        return jsonify({"status": "success", "message": "تم إضافة اللاعب بنجاح!"}), 200
    else:
        return jsonify({"status": "error", "message": "البيانات غير مكتملة!"}), 400

# تشغيل البوت
async def run_bot():
    """
    تهيئة البوت وتشغيله باستخدام Webhook.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder().token(token).build()

    # إعداد Webhook
    webhook_url = os.getenv("WEBHOOK_URL")  # تأكد من إضافة الرابط هنا
    application.bot.set_webhook(url=webhook_url)

    application.add_handler(CommandHandler("start", start))

    create_db()
    await application.run_webhook(
        listen="0.0.0.0",
        port=10000,  # تعديل المنفذ إلى 10000
        url_path="webhook",  # تأكد من إعداد هذا بشكل صحيح في Webhook URL
        webhook_url=f"{webhook_url}/webhook"
    )

# تشغيل تطبيق Flask باستخدام gunicorn
if __name__ == "__main__":
    from gunicorn.app.base import BaseApplication
    class FlaskApp(BaseApplication):
        def __init__(self, app):
            self.application = app
            super().__init__()

        def load(self):
            return self.application

    # تشغيل Flask باستخدام gunicorn
    flask_app = FlaskApp(app)
    flask_app.run()

    # تشغيل البوت
    asyncio.run(run_bot())
