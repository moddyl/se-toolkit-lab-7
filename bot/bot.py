import sys
import argparse
from handlers.commands import (
    handle_start, handle_help, handle_health,
    handle_scores, handle_labs, handle_unknown,
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
    elif text.startswith("/"):
        return handle_unknown(text)
    else:
        from services.llm_client import route
        return route(text)


def run_test_mode(command: str):
    response = dispatch(command)
    print(response)
    sys.exit(0)


def run_telegram_mode():
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler,
        CallbackQueryHandler, filters, ContextTypes,
    )
    from config import BOT_TOKEN

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📋 Labs", callback_data="labs"),
             InlineKeyboardButton("🏥 Health", callback_data="health")],
            [InlineKeyboardButton("📊 Scores lab-04", callback_data="scores_lab-04"),
             InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(handle_start(), reply_markup=reply_markup)

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_help())

    async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_health())

    async def scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = " ".join(context.args) if context.args else ""
        await update.message.reply_text(handle_scores(args))

    async def labs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_labs())

    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        if data == "labs":
            text = handle_labs()
        elif data == "health":
            text = handle_health()
        elif data == "help":
            text = handle_help()
        elif data.startswith("scores_"):
            lab = data[len("scores_"):]
            text = handle_scores(lab)
        else:
            text = handle_unknown(data)
        await query.edit_message_text(text)

    async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from services.llm_client import route
        text = update.message.text or ""
        response = route(text)
        await update.message.reply_text(response)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("scores", scores))
    app.add_handler(CommandHandler("labs", labs))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, metavar="COMMAND")
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()