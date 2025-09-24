from telegram import ForceReply, Update, File
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# from telegram import InlineKeyboardMarkup, InlineKeyboardButton # 互動式按鈕
from royabot.data_processing import process_stock_data
from pathlib import Path
from royabot import config
from loguru import logger


# 处理/start命令
def start(update, context):
    update.message.reply_text("Hi! Please send me an Excel file.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


# 处理接收到的文件
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(user)
    upload_file: File = await update.message.document.get_file()
    filename = update.message.document.file_name
    logger.info(filename)
    if not Path("downloads").exists():
        Path("downloads").mkdir(parents=True, exist_ok=True)

    await upload_file.download_to_drive(f"downloads/{filename}")
    latest_date = process_stock_data(
        f"downloads/{filename}", f"downloads/out_{filename}"
    )
    with open(f"downloads/out_{filename}", "rb") as f:
        await update.message.reply_document(
            document=f, caption=f"資料日期: {latest_date}."
        )


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(token=config.TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
