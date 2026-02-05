import asyncio

from telegram import ForceReply, Update, File
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from royabot.data_processing import process_stock_data
from royabot import config
from loguru import logger

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded document files."""
    try:
        user = update.message.from_user
        logger.info(f"Received document from user: {user.id} ({user.full_name})")

        filename = update.message.document.file_name
        suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            await update.message.reply_text(
                f"請上傳 Excel 檔案 (.xlsx / .xls)，目前收到: {suffix or '無副檔名'}"
            )
            return

        # Use user_id subdirectory to avoid filename collision
        user_dir = config.DOWNLOADS_DIR / str(user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        input_path = user_dir / filename
        output_path = user_dir / f"out_{filename}"

        upload_file: File = await update.message.document.get_file()
        await upload_file.download_to_drive(str(input_path))

        # Run blocking data processing in a thread to avoid blocking the event loop
        latest_date = await asyncio.to_thread(
            process_stock_data, str(input_path), str(output_path)
        )

        with open(str(output_path), "rb") as f:
            await update.message.reply_document(
                document=f, caption=f"資料日期: {latest_date}."
            )
    except Exception as e:
        logger.exception(f"Error processing document from user {update.message.from_user.id}")
        await update.message.reply_text("處理文件時發生錯誤，請稍後再試。")


def main() -> None:
    """Start the bot."""
    config.init_polars()

    application = Application.builder().token(token=config.TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
