from flask import Flask, request, render_template_string
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

BOT_TOKEN = "8160261655:AAFlIGI8lirPE4U5uLeBe_bah1tIktvzdSA"
OWNER_ID = 617739749
known_messages = {}  # message_id -> user_id

# === Flask-заглушка + простейшая панель ===
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>ZakBot работает ✅</h1><p>Панель в разработке...</p>"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === Старт-команда ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ZakBot включён. Пишите сюда.")

# === Автоответы по ключевым словам ===
AUTO_REPLIES = {
    "привет": "👋 Привет-привет!",
    "ты кто": "🤖 Я бот Zakviel, я пересылаю сообщения хозяину.",
}

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""

    # Сохраняем сообщение для кнопки "Ответить"
    known_messages[str(update.message.message_id)] = user.id

    # Автоответ по ключевым словам
    for trigger, reply in AUTO_REPLIES.items():
        if trigger in text.lower():
            await context.bot.send_message(chat_id=user.id, text=reply)
            break

    # Владелец пишет сам себе
    if user.id == OWNER_ID:
        await update.message.reply_text("🟢 Принял.")
        return

    # Переслать владельцу с кнопкой "Ответить"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Ответить", callback_data=f"reply:{user.id}:{update.message.message_id}")]
    ])

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📨 Сообщение от @{user.username or user.first_name} [{user.id}]:\n{text}",
        reply_markup=keyboard
    )

# === Обработка нажатия кнопки "Ответить" ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("reply:"):
        return

    parts = data.split(":")
    target_id = int(parts[1])

    await query.message.reply_text(f"✍️ Напиши, что отправить пользователю {target_id}.\nФормат:\n/re {target_id} текст")

# === Команда /re user_id сообщение ===
async def re_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❗ Пример: /re 123456789 Привет!")
        return

    user_id = int(context.args[0])
    message_text = ' '.join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=user_id, text=message_text)
        await update.message.reply_text("✅ Отправлено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# === Запуск бота ===
def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("re", re_cmd))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT, handle_msg))
    app_bot.run_polling()

# === Запуск Flask + Telegram ===
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_bot()