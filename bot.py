import os
import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
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
        conn = get_db_connection()
        if conn is None:
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
    finally:
        if conn:
            conn.close()

# إضافة لاعب إلى قاعدة البيانات
def add_player_to_db(player_name, player_image_url):
    try:
        conn = get_db_connection()
        if conn is None:
            return
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                           (player_name, player_image_url, 0))
            conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة اللاعب: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# تحديث تقدم لاعب
def update_player_progress(player_name, progress):
    try:
        conn = get_db_connection()
        if conn is None:
            return
        with conn.cursor() as cursor:
            cursor.execute("UPDATE players SET progress = %s WHERE name = %s", (progress, player_name))
            conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث التقدم: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# استرجاع تقدم لاعب
def get_player_progress(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT progress FROM players WHERE name = %s", (player_name,))
            progress = cursor.fetchone()
            return progress[0] if progress else 0
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع التقدم: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Play Game", web_app={"url": "https://twq-xzy4.onrender.com"})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحبًا! اضغط على الزر أدناه للعب:", reply_markup=reply_markup)

# تعريف الأمر /add_player
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("الاستخدام: /add_player <الاسم> <رابط الصورة>")
        return
    player_name, player_image_url = context.args[0], context.args[1]
    if not player_image_url.startswith(("http://", "https://")):
        await update.message.reply_text("رابط الصورة غير صالح.")
        return
    add_player_to_db(player_name, player_image_url)
    await update.message.reply_text(f"تم إضافة اللاعب {player_name} بنجاح!")

# تعريف أمر لعرض تقدم اللاعب
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("الاستخدام: /progress <الاسم>")
        return
    player_name = context.args[0]
    progress = get_player_progress(player_name)
    await update.message.reply_text(f"تقدم اللاعب {player_name}: {progress}%")

# تعريف أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    🤖 **قائمة الأوامر المتاحة:**
    🔹 `/start` - بدء استخدام البوت وعرض زر تشغيل اللعبة.
    🔹 `/add_player <الاسم> <رابط الصورة>` - إضافة لاعب جديد إلى قاعدة البيانات.
    🔹 `/progress <الاسم>` - عرض تقدم اللاعب المسجل في اللعبة.
    🔹 `/help` - عرض هذه القائمة.
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("help", help_command))
    create_db()
    application.run_polling()

if __name__ == "__main__":
    main()
