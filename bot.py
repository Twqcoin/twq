import os
import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse
import httpx

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# رابط صورة الترحيب من مستودع GitHub (استخدم الرابط RAW)
WELCOME_IMAGE_URL = "https://raw.githubusercontent.com/Twqcoin/twq/master/src/default_avatar.jpg.png"

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

async def download_image(url):
    """دالة مساعدة لتحميل الصورة من الرابط"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"فشل في تحميل الصورة من الرابط: {e}")
        return None

# تعريف الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    user_data = {
        "id": user.id,
        "name": user.full_name,
        "username": user.username if user.username else "no_username"
    }

    logger.info(f"البيانات المستلمة من اللاعب: {user_data}")

    bot_url = os.getenv("BOT_URL", "https://t.me/MinQX_Bot/MinQX")
    game_url = f"{bot_url}?user_id={user_data['id']}&name={user_data['name']}&username={user_data['username']}"

    keyboard = [[InlineKeyboardButton("Start", url=game_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال صورة الترحيب من المستودع
    try:
        # تحميل الصورة من مستودع GitHub
        image_content = await download_image(WELCOME_IMAGE_URL)
        
        if image_content:
            await update.message.reply_photo(
                photo=InputFile(image_content, filename="welcome.png"),
                caption=f"🎉 أهلاً بك {user.first_name} في MINQX!",
                reply_markup=reply_markup
            )
        else:
            # إذا فشل تحميل الصورة، أرسل رسالة نصية
            await update.message.reply_text(
                f"🎉 أهلاً بك {user.first_name} في MINQX!",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة الترحيب: {e}")
        await update.message.reply_text(
            f"🎉 أهلاً بك {user.first_name} في MINQX!",
            reply_markup=reply_markup
        )

# معالج الأخطاء
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"حدث خطأ أثناء معالجة التحديث: {context.error}", exc_info=context.error)

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)

    try:
        logger.info("تشغيل البوت باستخدام Polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
