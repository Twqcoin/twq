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
                                    progress INTEGER DEFAULT 0)''')
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
                cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                               (player_name, player_image_url, 0))
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة اللاعب: {e}", exc_info=True)

# تحديث تقدم لاعب
def update_player_progress(player_name, progress):
    """
    تحديث تقدم لاعب في قاعدة البيانات.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن تحديث التقدم. لم يتم الاتصال بقاعدة البيانات.")
                return

            with conn.cursor() as cursor:
                cursor.execute("UPDATE players SET progress = %s WHERE name = %s", (progress, player_name))
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث التقدم: {e}", exc_info=True)

# استرجاع تقدم لاعب
def get_player_progress(player_name):
    """
    استرجاع تقدم لاعب من قاعدة البيانات.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن استرجاع التقدم. لم يتم الاتصال بقاعدة البيانات.")
                return None

            with conn.cursor() as cursor:
                cursor.execute("SELECT progress FROM players WHERE name = %s", (player_name,))
                progress = cursor.fetchone()
                return progress[0] if progress else None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع التقدم: {e}", exc_info=True)
        return None

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    بدء استخدام البوت وعرض زر "Play Game".
    """
    keyboard = [
        [InlineKeyboardButton(
            text="Play Game",
            web_app={"url": "https://twq.onrender.com"}
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "مرحبًا! اضغط على الزر أدناه للعب:",
        reply_markup=reply_markup
    )

# تعريف الأمر /add_player
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إضافة لاعب جديد إلى قاعدة البيانات.
    """
    try:
        player_name = context.args[0] if context.args else None
        player_image_url = context.args[1] if len(context.args) > 1 else None

        if not player_name or not player_image_url:
            await update.message.reply_text("الاستخدام: /add_player <الاسم> <رابط الصورة>")
            return

        if not player_image_url.startswith(("http://", "https://")):
            await update.message.reply_text("رابط الصورة غير صالح. يجب أن يبدأ بـ http:// أو https://")
            return

        add_player_to_db(player_name, player_image_url)
        await update.message.reply_text(f"تم إضافة اللاعب {player_name} بنجاح!")
    except Exception as e:
        logger.error(f"حدث خطأ: {e}", exc_info=True)
        await update.message.reply_text("حدث خطأ أثناء إضافة اللاعب.")

# تعريف أمر لعرض تقدم اللاعب
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض تقدم لاعب من قاعدة البيانات.
    """
    try:
        player_name = context.args[0] if context.args else None
        if not player_name:
            await update.message.reply_text("الاستخدام: /progress <الاسم>")
            return

        progress = get_player_progress(player_name)
        if progress is None:
            await update.message.reply_text(f"لم يتم العثور على اللاعب {player_name}.")
        else:
            await update.message.reply_text(f"تقدم اللاعب {player_name}: {progress}%")
    except Exception as e:
        logger.error(f"حدث خطأ: {e}", exc_info=True)
        await update.message.reply_text("حدث خطأ أثناء استرجاع التقدم.")

# تعريف أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض قائمة بالأوامر المتاحة.
    """
    help_text = """
    الأوامر المتاحة:
    /start - بدء استخدام البوت
    /add_player <الاسم> <رابط الصورة> - إضافة لاعب جديد
    /progress <الاسم> - عرض تقدم لاعب
    /help - عرض هذه الرسالة
    """
    await update.message.reply_text(help_text)

# تعريف أمر /test_db
async def test_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    اختبار الاتصال بقاعدة البيانات.
    """
    conn = get_db_connection()
    if conn:
        await update.message.reply_text("تم الاتصال بقاعدة البيانات بنجاح!")
        conn.close()
    else:
        await update.message.reply_text("فشل الاتصال بقاعدة البيانات.")

# تشغيل البوت
def main():
    """
    تهيئة البوت وبدء التشغيل.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder() \
        .token(token) \
        .build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("test_db", test_db))

    create_db()
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
