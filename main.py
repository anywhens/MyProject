from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7912549689:AAG8YzmSHfcaJoy2TBWLhv_baI9OaS7JpN8"
ADMIN_ID = 6444944021  # Замените на свой ID

user_context = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте сообщение, и оно будет переслано администратору.")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    username = update.message.chat.username or "Без имени"
    message_text = update.message.text

    user_context[user_id] = username  # Сохраняем связь пользователя

    # Отправляем сообщение администратору
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новое сообщение от @{username} (ID: {user_id}):\n{message_text}"
    )
    await update.message.reply_text("Ваше сообщение отправлено администратору.")

async def reply_to_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ADMIN_ID:
        await update.message.reply_text("Эта команда доступна только администратору.")
        return

    try:
        # Проверяем, что есть аргументы
        if len(context.args) < 2:
            await update.message.reply_text("Использование: /reply <ID пользователя> <текст ответа>")
            return

        # Извлекаем ID пользователя и текст ответа
        user_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])

        # Отправляем сообщение пользователю
        await context.bot.send_message(chat_id=user_id, text=f"Ответ от администратора: {reply_text}")
        await update.message.reply_text("Ответ отправлен пользователю.")
    except ValueError:
        await update.message.reply_text("Некорректный ID пользователя.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке сообщения: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    application.add_handler(CommandHandler("reply", reply_to_user_command))

    application.run_polling()

if __name__ == "__main__":
    main()
