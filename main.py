from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "ваш_токен_бота"   # Замените на свой токен бота
ADMIN_ID = "ваш_telegram_id"  # Замените на свой ID

user_context = {}
waiting_for_message = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Привет! Нажмите на кнопку ниже, чтобы отправить сообщение администратору:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ *Справка по боту* ℹ️"
        "📩 *Отправка сообщения администратору:*"
        "- Нажмите на кнопку '📩 Отправить сообщение администратору'."
        "- Введите ваше сообщение и отправьте его."
        "- Дождитесь ответа от администратора."
        "🛠 *Команды:*"
        "/start - Начать работу с ботом"
        "/help - Получить справку"
        "(Администратор) /reply <ID пользователя> <сообщение> - Ответить пользователю"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.message.chat.id
    await query.answer()
    waiting_for_message.add(user_id)  # Добавляем пользователя в список тех, кто нажал кнопку
    await query.message.edit_text(
        "✍ Введите ваше сообщение и отправьте его.",
        reply_markup=None  # Убираем кнопку после нажатия
    )

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id not in waiting_for_message:
        await update.message.reply_text("⚠️ Сначала нажмите на кнопку '📩 Отправить сообщение администратору'.")
        return

    username = update.message.chat.username or "Без имени"
    message_text = update.message.text

    user_context[user_id] = username  # Сохраняем связь пользователя
    waiting_for_message.remove(user_id)  # Убираем из списка после отправки

    # Отправляем сообщение администратору
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📬 Новое сообщение от @{username} (ID: {user_id}):\n{message_text}"
    )
    await update.message.reply_text("✅ Ваше сообщение успешно отправлено, ожидайте ответа.")

async def reply_to_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return

    try:
        # Проверяем, что есть аргументы
        if len(context.args) < 2:
            await update.message.reply_text("⚠️ Использование: /reply <ID пользователя> <текст ответа>")
            return

        # Извлекаем ID пользователя и текст ответа
        user_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])

        # Отправляем сообщение пользователю
        await context.bot.send_message(chat_id=user_id, text=f"💬 Ответ от администратора: {reply_text}")
        await update.message.reply_text("✅ Ответ отправлен пользователю.")
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID пользователя.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при отправке сообщения: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="send_message"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.add_handler(CommandHandler("reply", reply_to_user_command))

    application.run_polling()

if __name__ == "__main__":
    main()
