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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
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
    user = update.effective_user
    bot = context.bot

    user_data = {
        "id": user.id,
        "name": user.full_name,
        "username": user.username if user.username else "no_username",
    }

    # محاولة جلب صورة المستخدم
    try:
        photos = await bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            photo_file = await bot.get_file(photos.photos[0][-1].file_id)
            photo_url = photo_file.file_path
        else:
            photo_url = "https://example.com/default_avatar.jpg"
    except Exception as e:
        logger.error(f"خطأ في تحميل صورة المستخدم: {e}")
        photo_url = "https://example.com/default_avatar.jpg"

    user_data["photo"] = photo_url

    logger.info(f"البيانات المستلمة من اللاعب: {user_data}")

    bot_url = os.getenv("BOT_URL", "https://t.me/MinQX_Bot/MinQX")
    game_url = f"{bot_url}?user_id={user_data['id']}&name={user_data['name']}&username={user_data['username']}&photo={user_data['photo']}"

    keyboard = [[InlineKeyboardButton("Start", url=game_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال الصورة مع الزر
    if "https://" in photo_url or "http://" in photo_url:
        await update.message.reply_photo(photo=photo_url, caption="👤 Welcome to MINQX", reply_markup=reply_markup)
    else:
        await update.message.reply_text("👤 Welcome to MINQX", reply_markup=reply_markup)

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    try:
        logger.info("تشغيل البوت باستخدام Polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
