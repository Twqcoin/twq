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
            database=result.path[1:],  # استبعاد أول / في الـ path
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,  # إذا كان المنفذ غير موجود في الرابط، سيتم استخدام المنفذ الافتراضي 5432
            sslmode='require',  # تأكد من أن SSL مفعل
            sslrootcert=certifi.where()  # استخدام شهادات SSL موثوقة
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
            logger.error("لا يمكن إنشاء قاعدة البيانات. لم يتم الاتصال بالخادم.")
            return

        with conn.cursor() as cursor:
            # إنشاء جدول لتخزين بيانات اللاعبين
            cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                                id SERIAL PRIMARY KEY,
                                name TEXT NOT NULL,
                                image_url TEXT NOT NULL,
                                progress INTEGER DEFAULT 0)''')
            conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء الجدول: {e}", exc_info=True)

# إضافة لاعب إلى قاعدة البيانات
def add_player_to_db(player_name, player_image_url):
    """
    إضافة لاعب جديد إلى قاعدة البيانات.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("لا يمكن إضافة اللاعب. لم يتم الاتصال بقاعدة البيانات.")
            return

        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                           (player_name, player_image_url, 0))  # 0 تعني تقدم اللاعب الأولي
            conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة اللاعب: {e}", exc_info=True)

# تحديث تقدم لاعب
def update_player_progress(player_name, progress):
    """
    تحديث تقدم لاعب في قاعدة البيانات.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("لا يمكن تحديث التقدم. لم يتم الاتصال بقاعدة البيانات.")
            return

        with conn.cursor() as cursor:
            cursor.execute("UPDATE players SET progress = %s WHERE name = %s", (progress, player_name))
            conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث التقدم: {e}", exc_info=True)

# استرجاع تقدم لاعب
def get_player_progress(player_name):
    """
    استرجاع تقدم لاعب من قاعدة البيانات.
    """
    try:
        conn = get_db_connection()
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
    # إنشاء زر "Play Game" مع الرابط الخاص بـ Web App
    keyboard = [
        [InlineKeyboardButton(
            text="Play Game",
            web_app={"url": "https://twq-xzy4.onrender.com"}  # رابط التطبيق الذي تريد فتحه داخل Telegram
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال الرسالة مع الزر
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
        # الحصول على بيانات اللاعب من الرسالة
        player_name = context.args[0] if context.args else None
        player_image_url = context.args[1] if len(context.args) > 1 else None

        if not player_name or not player_image_url:
            await update.message.reply_text("الاستخدام: /add_player <الاسم> <رابط الصورة>")
            return

        # تحقق من أن player_image_url هو رابط صحيح
        if not player_image_url.startswith(("http://", "https://")):
            await update.message.reply_text("رابط الصورة غير صالح. يجب أن يبدأ بـ http:// أو https://")
            return

        # إضافة اللاعب إلى قاعدة البيانات
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

# تشغيل البوت
def main():
    """
    تهيئة البوت وبدء التشغيل.
    """
    # تهيئة البوت
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder().token(token).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("help", help_command))

    # تأكد من أن قاعدة البيانات موجودة
    create_db()

    # بدء البوت
    application.run_polling()

if __name__ == "__main__":
    main()
