import os
import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from urllib.parse import urlparse
import httpx

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Welcome image URL from GitHub repository (using RAW link)
WELCOME_IMAGE_URL = "https://raw.githubusercontent.com/Twqcoin/twq/master/src/default_avatar.jpg.png"

# Database connection setup
def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not found in environment variables")
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
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        return None

async def download_image(url):
    """Helper function to download image from URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Failed to download image from URL: {e}")
        return None

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    user_data = {
        "id": user.id,
        "name": user.full_name,
        "username": user.username if user.username else "no_username"
    }

    logger.info(f"User data received: {user_data}")

    bot_url = os.getenv("BOT_URL", "https://t.me/MinQX_Bot/MinQX")
    game_url = f"{bot_url}?user_id={user_data['id']}&name={user_data['name']}&username={user_data['username']}"

    keyboard = [[InlineKeyboardButton("Start", url=game_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send welcome image from repository
    try:
        # Download image from GitHub repository
        image_content = await download_image(WELCOME_IMAGE_URL)
        
        if image_content:
            await update.message.reply_photo(
                photo=InputFile(image_content, filename="welcome.png"),
                caption=f"🎉 Welcome {user.first_name} to MINQX!",
                reply_markup=reply_markup
            )
        else:
            # If image download fails, send text message
            await update.message.reply_text(
                f"🎉 Welcome {user.first_name} to MINQX!",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")
        await update.message.reply_text(
            f"🎉 Welcome {user.first_name} to MINQX!",
            reply_markup=reply_markup
        )

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error while processing update: {context.error}", exc_info=context.error)

# Start the bot
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Bot token not found in environment variables")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_error_handler(error_handler)

    try:
        logger.info("Starting bot using polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()
