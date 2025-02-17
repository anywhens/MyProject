import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "ваш_токен_бота"   # Замените на свой токен бота
ADMIN_ID = int("ваш_telegram_id")  # Замените на свой ID
waiting_for_message = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_needed_files_and_folders()
    keyboard = [
        [InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")],
        [InlineKeyboardButton("🔧 Частые проблемы", callback_data="common_issues")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Привет! Выберите действие:", reply_markup=reply_markup
    )

async def show_common_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("💻 Не включается компьютер", callback_data="issue_1")],
        [InlineKeyboardButton("🌐 Нет интернета", callback_data="issue_2")],
        [InlineKeyboardButton("🖨 Принтер не печатает", callback_data="issue_3")],
        [InlineKeyboardButton("🔊 Нет звука на ПК", callback_data="issue_4")],
        [InlineKeyboardButton("⌨️ Клавиатура не работает", callback_data="issue_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Выберите проблему:", reply_markup=reply_markup)

async def issue_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    solutions = {
        "issue_1": "🔌 Проверьте кабель питания и подключение. Попробуйте другой разъем.",
        "issue_2": "📶 Перезагрузите роутер и проверьте настройки сети.",
        "issue_3": "🖨 Проверьте картриджи, подключение и попробуйте перезапустить принтер.",
        "issue_4": "🔉 Проверьте уровень громкости и драйверы звуковой карты.",
        "issue_5": "⌨️ Проверьте подключение клавиатуры и попробуйте перезагрузить ПК."
    }
    await query.message.edit_text(solutions.get(query.data, "Ошибка: проблема не найдена."))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "send_message":
        user_id = query.message.chat.id
        waiting_for_message.add(user_id)
        await query.answer()
        await query.message.edit_text("✍ Введите ваше сообщение для администратора.")
    elif query.data == "common_issues":
        await show_common_issues(update, context)
    elif query.data.startswith("issue_"):
        await issue_solution(update, context)

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in waiting_for_message:
        await update.message.reply_text("⚠️ Сначала нажмите на кнопку '📩 Отправить сообщение администратору'.")
        return
    waiting_for_message.remove(user_id)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📬 Новое сообщение от {update.message.chat.username or 'Без имени'} (ID: {user_id}):\n{update.message.text}"
    )
    await update.message.reply_text("✅ Ваше сообщение отправлено администратору.")

async def reply_to_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return
    try:
        if len(context.args) < 2:
            await update.message.reply_text("⚠️ Использование: /reply <ID пользователя> <текст ответа>")
            return
        user_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"💬 Ответ от администратора: {reply_text}")
        await update.message.reply_text("✅ Ответ отправлен пользователю.")
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID пользователя.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при отправке сообщения: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ *Справка по боту* ℹ️\n"
        "📩 *Отправка сообщения администратору:*\n"
        "- Нажмите на кнопку '📩 Отправить сообщение администратору'.\n"
        "- Введите ваше сообщение и отправьте его.\n"
        "🔧 *Частые проблемы:*\n"
        "- Нажмите '🔧 Частые проблемы' и выберите нужную вам проблему."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reply", reply_to_user_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.run_polling()

if __name__ == "__main__":
    main()
