import os
import logging
import psycopg2
import certifi
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد اتصال بقاعدة بيانات PostgreSQL
def get_db_connection():
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
                                    progress INTEGER DEFAULT 0)''')
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء الجدول: {e}", exc_info=True)

# إضافة لاعب إلى قاعدة البيانات
def add_player_to_db(player_name, player_image_url):
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

# استلام بيانات اللاعب عند الضغط على "Play Game" داخل اللعبة
@app.route("/receive_player_data", methods=["POST"])
def receive_player_data():
    player_data = request.json
    player_name = player_data.get("name")
    player_image_url = player_data.get("image_url")
    
    if player_name and player_image_url:
        add_player_to_db(player_name, player_image_url)
        return jsonify({"status": "success", "message": "تم إضافة اللاعب بنجاح!"}), 200
    else:
        return jsonify({"status": "error", "message": "البيانات غير مكتملة!"}), 400

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            text="Play Game",
            web_app={"url": "https://twq-xzy4.onrender.com"}  # رابط اللعبة هنا
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "مرحبًا! اضغط على الزر أدناه للعب:",
        reply_markup=reply_markup
    )

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder() \
        .token(token) \
        .build()

    application.add_handler(CommandHandler("start", start))

    create_db()
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
