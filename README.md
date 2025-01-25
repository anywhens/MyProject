**Telegram Bot для отправки сообщений администратору**

Этот бот создан для передачи сообщений от пользователей администратору. Администратор может отвечать на эти сообщения с помощью специальной команды бота. Бот построен на базе библиотеки python-telegram-bot.

**Основные функции**

1. Пользователь может отправить сообщение боту, которое будет переслано администратору.
2. Администратор может ответить на сообщение пользователя с помощью команды /reply.

**Установка**

**Шаг 1. Склонируйте репозиторий**

git clone https://github.com/your-repo-name/telegram-admin-bot.git

cd telegram-admin-bot

**Шаг 2. Установите зависимости**

Создайте виртуальное окружение и установите зависимости:

python -m venv venv

source venv/bin/activate  # Для Windows используйте: venv\Scripts\activate

pip install -r requirements.txt

**Шаг 3. Настройте переменные окружения**

BOT_TOKEN=ваш_токен_бота

ADMIN_ID=ваш_telegram_id

Узнать свой Telegram ID можно, написав любому боту, например, @userinfobot.

**Шаг 4. Запустите бота**

python main.py

**Использование**

**Для пользователя:**
1. Напишите любое сообщение боту.
2. Бот пересылает сообщение администратору.
3. Получите ответ от администратора, если он решит ответить.

**Для администратора:**
1. Получите сообщение от пользователя с указанием его ID.
2. Ответьте пользователю с помощью команды: /reply <ID пользователя> <текст ответа>

Пример:

/reply 123456789 Привет! Спасибо за ваше сообщение.

Бот отправит указанному пользователю ваш ответ.
