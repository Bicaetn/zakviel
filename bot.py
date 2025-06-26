from flask import Flask
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from datetime import datetime

# === Настройки ===
BOT_TOKEN = "8160261655:AAFlIGI8lirPE4U5uLeBe_bah1tIktvzdSA"
OWNER_ID = 617739749

# === Логирование в файл ===
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# === Flask-заглушка для Render ===
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и работает на Render!")

# === Команда /ответ <id> <сообщение> (только для владельца) ===
async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❗ Пример: /ответ 123456789 Привет!")
        return

    user_id = int(context.args[0])
    message_text = ' '.join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=message_text)
        await update.message.reply_text(f"✅ Отправлено пользователю {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# === Обработка всех сообщений ===
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""

    # Лог в файл
    logging.info(f"From {user.id} ({user.username}): {text}")

    # Если пишет владелец
    if user.id == OWNER_ID:
        await update.message.reply_text("🟢 Принял.")
        return

    # Автоответ
    if "привет" in text.lower():
        await context.bot.send_message(chat_id=user.id, text="👋 Привет!")

    # Переслать владельцу
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📨 От @{user.username or user.first_name} [{user.id}]:\n{text}"
    )

# === Запуск бота ===
def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("ответ", reply_cmd))
    app_bot.add_handler(MessageHandler(filters.TEXT, handle_msg))
    app_bot.run_polling()

# === Запуск Flask и бота ===
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_bot()
