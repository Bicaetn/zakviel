from flask import Flask
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8160261655:AAFlIGI8lirPE4U5uLeBe_bah1tIktvzdSA"
OWNER_ID = 617739749

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот жив!")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id == OWNER_ID:
        await update.message.reply_text("🟢 Принял.")
    else:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📨 От @{user.username or user.first_name}:\n{text}"
        )

def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT, handle_msg))
    app_bot.run_polling()