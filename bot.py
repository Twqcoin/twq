import os
import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

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
    user = update.effective_user
    user_data = {
        "id": user.id,
        "name": user.full_name,
        "username": user.username if user.username else "لا يوجد اسم مستخدم",
    }

    # استرجاع صورة البروفايل باستخدام API
    try:
        user_profile_photos = await update.effective_user.get_profile_photos()
        if user_profile_photos.total_count > 0:
            # استخدام أول صورة تم العثور عليها
            photo_url = f"https://t.me/i/userpic/{user.id}_{user_profile_photos.photos[0][-1].file_id}.jpg"
        else:
            photo_url = "https://example.com/default_avatar.jpg"  # صورة افتراضية إذا لم تكن هناك صورة
    except Exception as e:
        logger.error(f"فشل في جلب صورة المستخدم: {e}")
        photo_url = "https://example.com/default_avatar.jpg"  # صورة افتراضية إذا حدث خطأ

    user_data["photo"] = photo_url
    
    # طباعة بيانات اللاعب للتحقق
    logger.info(f"البيانات المستلمة من اللاعب: {user_data}")

    # بناء رابط اللعبة
    game_url = f"https://twq-xzy4.onrender.com?user_id={user_data['id']}&name={user_data['name']}&username={user_data['username']}&photo={user_data['photo']}"
    
    # إعداد الزر الذي يحتوي على رابط اللعبة
    keyboard = [[InlineKeyboardButton("Play Game", web_app={"url": game_url})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال رسالة الترحيب مع رابط اللعبة
    await update.message.reply_text("مرحبًا! اضغط على الزر أدناه للعب:", reply_markup=reply_markup)

# إعداد Webhook للبوت
def set_webhook():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")  # تأكد من أن لديك URL البوت
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}/webhook"
    response = requests.post(url)
    if response.status_code == 200:
        logger.info("تم إعداد Webhook بنجاح!")
    else:
        logger.error("فشل في إعداد Webhook")

# الحصول على معلومات Webhook
def get_webhook_info():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    response = requests.get(url)
    logger.info(response.json())

# تشغيل البوت
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على رمز البوت في المتغيرات البيئية.")
        return

    # تعيين Webhook عند بدء التطبيق
    set_webhook()

    # التحقق من Webhook الحالي
    get_webhook_info()

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()
