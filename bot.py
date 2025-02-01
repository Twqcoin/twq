import os
import logging
import psycopg2
import certifi
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse
from threading import Thread

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

# تحديث تقدم التعدين
def update_mining_progress(player_name, mining_progress):
    """
    تحديث تقدم التعدين للاعب.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن تحديث التقدم. لم يتم الاتصال بقاعدة البيانات.")
                return

            with conn.cursor() as cursor:
                cursor.execute("UPDATE players SET mining_progress = %s WHERE name = %s", (mining_progress, player_name))
                conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث تقدم التعدين: {e}", exc_info=True)

# تحديث المهام المكتملة
def update_tasks_completed(player_name, task):
    """
    تحديث المهام المكتملة للاعب.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن تحديث المهام المكتملة. لم يتم الاتصال بقاعدة البيانات.")
                return

            with conn.cursor() as cursor:
                cursor.execute("SELECT tasks_completed FROM players WHERE name = %s", (player_name,))
                tasks = cursor.fetchone()
                if tasks:
                    tasks_completed = tasks[0]
                    if task not in tasks_completed:
                        tasks_completed += f", {task}"
                    cursor.execute("UPDATE players SET tasks_completed = %s WHERE name = %s", (tasks_completed, player_name))
                    conn.commit()
                else:
                    logger.error(f"لا توجد بيانات للاعب {player_name}.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث المهام المكتملة: {e}", exc_info=True)

# استرجاع المهام المكتملة
def get_player_tasks(player_name):
    """
    استرجاع المهام المكتملة للاعب.
    """
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("لا يمكن استرجاع المهام. لم يتم الاتصال بقاعدة البيانات.")
                return None

            with conn.cursor() as cursor:
                cursor.execute("SELECT tasks_completed FROM players WHERE name = %s", (player_name,))
                tasks = cursor.fetchone()
                return tasks[0] if tasks else None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع المهام: {e}", exc_info=True)
        return None

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

# تعريف أمر /progress
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض تقدم اللاعب في اللعبة.
    """
    player_name = update.message.text.split(' ')[1]
    progress = get_player_progress(player_name)
    mining_progress = get_player_mining_progress(player_name)

    if progress is None:
        await update.message.reply_text(f"لا يوجد تقدم للاعب {player_name}.")
    else:
        await update.message.reply_text(f"تقدم اللاعب {player_name}: {progress}% في اللعبة، {mining_progress}% في التعدين.")

# تعريف أمر /tasks
async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض المهام المكتملة للاعب.
    """
    player_name = update.message.text.split(' ')[1]
    tasks_completed = get_player_tasks(player_name)

    if tasks_completed:
        await update.message.reply_text(f"المهام المكتملة للاعب {player_name}: {tasks_completed}.")
    else:
        await update.message.reply_text(f"لا توجد مهام مكتملة للاعب {player_name}.")

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
    /tasks <الاسم> - عرض المهام المكتملة للاعب
    /help - عرض هذه الرسالة
    """
    await update.message.reply_text(help_text)

# تشغيل البوت
def main():
    """
    تهيئة البوت وبدء التشغيل باستخدام Webhook.
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("tasks", tasks))

    create_db()
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5432)),  # تأكد من أن المنفذ صحيح
        url_path="webhook",  # تأكد من إعداد هذا بشكل صحيح في Webhook URL
        webhook_url=f"{webhook_url}/webhook"
    )

# تشغيل Flask في الخلفية
if __name__ == "__main__":
    # تشغيل Flask في الخلفية
    def run_flask():
        port = os.getenv("PORT", 5432)  # تحديد المنفذ باستخدام المتغير البيئي PORT
        app.run(debug=True, host="0.0.0.0", port=int(port), use_reloader=False)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # تشغيل البوت
    main()
