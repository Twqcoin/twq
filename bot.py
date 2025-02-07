import os
import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import requests

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد اتصال بقاعدة بيانات PostgreSQL
def get_db_connection():
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

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Play Game", web_app={"url": "https://your-app-name.onrender.com"})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحبًا! اضغط على الزر أدناه للعب:", reply_markup=reply_markup)

# تعريف أمر لبدء التعدين
async def start_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("الاستخدام: /start_mining <userId>")
        return
    user_id = context.args[0]
    try:
        response = requests.post("https://your-app-name.onrender.com/start-mining", json={"userId": user_id})
        if response.status_code == 200:
            await update.message.reply_text("تم بدء التعدين بنجاح!")
        else:
            await update.message.reply_text("حدث خطأ أثناء بدء التعدين.")
    except Exception as e:
        logger.error(f"خطأ في الاتصال بـ API: {e}")
        await update.message.reply_text("حدث خطأ أثناء الاتصال بـ API.")

# تعريف أمر لإضافة إحالة
async def add_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("الاستخدام: /add_referral <userId>")
        return
    user_id = context.args[0]
    try:
        response = requests.post("https://twq-xzy4.onrender.com/add-referral", json={"userId": user_id})
        if response.status_code == 200:
            await update.message.reply_text("تم إضافة الإحالة بنجاح!")
        else:
            await update.message.reply_text("حدث خطأ أثناء إضافة الإحالة.")
    except Exception as e:
        logger.error(f"خطأ في الاتصال بـ API: {e}")
        await update.message.reply_text("حدث خطأ أثناء الاتصال بـ API.")

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("start_mining", start_mining))
    application.add_handler(CommandHandler("add_referral", add_referral))
    application.run_polling()

if __name__ == "__main__":
    main()
