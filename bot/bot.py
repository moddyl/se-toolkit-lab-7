import sys
import argparse
from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_scores,
    handle_labs,
    handle_unknown,
)


def dispatch(text: str) -> str:
    text = text.strip()
    if text == "/start":
        return handle_start()
    elif text == "/help":
        return handle_help()
    elif text == "/health":
        return handle_health()
    elif text.startswith("/scores"):
        args = text[len("/scores"):].strip()
        return handle_scores(args)
    elif text == "/labs":
        return handle_labs()
    else:
        return handle_unknown(text)


def run_test_mode(command: str):
    response = dispatch(command)
    print(response)
    sys.exit(0)


def run_telegram_mode():
    import asyncio
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
    from config import BOT_TOKEN

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_start())

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_help())

    async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_health())

    async def scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = " ".join(context.args) if context.args else ""
        await update.message.reply_text(handle_scores(args))

    async def labs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_labs())

    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_unknown(update.message.text))

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("scores", scores))
    app.add_handler(CommandHandler("labs", labs))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, metavar="COMMAND", help="Run in test mode")
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()