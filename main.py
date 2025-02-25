import os
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "ваш_токен_бота"   # Замените на свой токен бота
ADMIN_ID = int("ваш_telegram_id")  # Замените на свой ID

waiting_for_message = set()
user_data = {}  # Хранит данные пользователей: {user_id: {'name', 'surname', 'group'}}
registering_users = {}  # Отслеживает процесс регистрации: {user_id: {'step': 'name'}}

# Функции для работы с базой данных
def init_db():
    """Инициализирует базу данных и создает таблицу, если она не существует"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  name TEXT NOT NULL, 
                  surname TEXT NOT NULL, 
                  group_name TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def load_users():
    """Загружает всех пользователей из базы данных в user_data"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id, name, surname, group_name FROM users')
    users = {}
    for row in c.fetchall():
        user_id, name, surname, group_name = row
        users[user_id] = {
            'name': name,
            'surname': surname,
            'group': group_name
        }
    conn.close()
    return users

def save_user(user_id, name, surname, group_name):
    """Сохраняет или обновляет пользователя в базе данных"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
                 (user_id, name, surname, group_name) 
                 VALUES (?, ?, ?, ?)''',
              (user_id, name, surname, group_name))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Регистрация", callback_data="register")],
        [InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")],
        [InlineKeyboardButton("🔧 Частые проблемы", callback_data="common_issues")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Привет! Выберите действие:", reply_markup=reply_markup
    )

async def show_common_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in user_data:
        await query.answer("⛔ Пожалуйста, зарегистрируйтесь, чтобы использовать бота.", show_alert=True)
        return
    
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
    user_id = query.from_user.id
    
    if user_id not in user_data:
        await query.answer("⛔ Пожалуйста, зарегистрируйтесь, чтобы использовать бота.", show_alert=True)
        return
    
    solutions = {
        "issue_1": "🔌 Проверьте кабель питания и подключение. Попробуйте другой разъем.",
        "issue_2": "📶 Перезагрузите роутер и проверьте настройки сети.",
        "issue_3": "🖨 Проверьте картриджи, подключение и попробуйте перезапустить принтер.",
        "issue_4": "🔉 Проверьте уровень громкости и драйверы звуковой карты.",
        "issue_5": "⌨️ Проверьте подключение клавиатуры и попробуйте перезагрузить ПК."
    }
    
    solution_text = solutions.get(query.data, "Ошибка: проблема не найдена.")
    additional_text = "Если здесь нет решения вашей проблемы, напишите администратору о вашей проблеме указав кабинет в котором она имеется."
    
    keyboard = [[InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(f"{solution_text}\n\n{additional_text}", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "send_message":
        if user_id not in user_data:
            await query.answer("⛔ Пожалуйста, зарегистрируйтесь, чтобы использовать бота.", show_alert=True)
            return
        
        waiting_for_message.add(user_id)
        await query.answer()
        await query.message.edit_text("✍ Введите ваше сообщение для администратора.")
    
    elif query.data == "common_issues":
        await show_common_issues(update, context)
    
    elif query.data.startswith("issue_"):
        await issue_solution(update, context)
    
    elif query.data == "register":
        if user_id in waiting_for_message:
            waiting_for_message.remove(user_id)
        registering_users[user_id] = {'step': 'name'}
        await query.answer()
        await context.bot.send_message(chat_id=user_id, text="Введите ваше имя:")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text

    # Обработка регистрации
    if user_id in registering_users:
        step = registering_users[user_id].get('step')
        
        if step == 'name':
            registering_users[user_id]['name'] = text
            registering_users[user_id]['step'] = 'surname'
            await update.message.reply_text("Введите вашу фамилию:")
            return
        
        elif step == 'surname':
            registering_users[user_id]['surname'] = text
            registering_users[user_id]['step'] = 'group'
            await update.message.reply_text("Введите вашу группу:")
            return
        
        elif step == 'group':
            # Сохраняем пользователя в базу данных и обновляем user_data
            name = registering_users[user_id]['name']
            surname = registering_users[user_id]['surname']
            group = text
            
            save_user(user_id, name, surname, group)
            user_data[user_id] = {
                'name': name,
                'surname': surname,
                'group': group
            }
            
            del registering_users[user_id]
            await update.message.reply_text("✅ Регистрация завершена!")
            
            # Показываем главное меню
            keyboard = [
                [InlineKeyboardButton("📝 Регистрация", callback_data="register")],
                [InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")],
                [InlineKeyboardButton("🔧 Частые проблемы", callback_data="common_issues")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("👋 Выберите действие:", reply_markup=reply_markup)
            return

    # Обработка сообщений для администратора
    if user_id in waiting_for_message:
        waiting_for_message.remove(user_id)
        
        # Формируем сообщение для администратора
        user_info = user_data.get(user_id, {})
        username = f"@{update.message.chat.username}" if update.message.chat.username else "Без имени"
        
        if user_info:
            user_text = f"{user_info['name']} {user_info['surname']}, группа {user_info['group']}, {username}"
        else:
            user_text = f"{username}"
        
        admin_message = (
            f"📬 Новое сообщение от {user_text}\n"
            f"ID: {user_id}\n"
            f"Сообщение: {text}"
        )
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
        await update.message.reply_text("✅ Ваше сообщение отправлено администратору.")
        
        # Возвращаем в главное меню
        keyboard = [
            [InlineKeyboardButton("📝 Регистрация", callback_data="register")],
            [InlineKeyboardButton("📩 Отправить сообщение администратору", callback_data="send_message")],
            [InlineKeyboardButton("🔧 Частые проблемы", callback_data="common_issues")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("👋 Выберите действие:", reply_markup=reply_markup)
        return

    # Если не регистрация и не сообщение администратору
    await update.message.reply_text("ℹ Пожалуйста, используйте кнопки меню для взаимодействия с ботом.")

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
        "ℹ Справка по боту:\n"
        "📩 Отправка сообщения администратору:\n"
        "- Нажмите на кнопку '📩 Отправить сообщение администратору'\n"
        "- Введите ваше сообщение и отправьте его\n\n"
        "🔧 Частые проблемы:\n"
        "- Нажмите '🔧 Частые проблемы' и выберите нужную вам проблему\n\n"
        "📝 Регистрация:\n"
        "- Нажмите '📝 Регистрация' и следуйте инструкциям"
    )
    await update.message.reply_text(help_text)

def main():
    # Инициализация базы данных и загрузка пользователей
    init_db()
    global user_data
    user_data = load_users()  # Загружаем пользователей из базы при старте
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reply", reply_to_user_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()