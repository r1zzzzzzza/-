import telebot
import json
import os


import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="AlicaMi359219",
    host="localhost",
    port=5432,
)
cur = conn.cursor()


# Токен вашего бота
token = '7400367270:AAGkvpEaDXGZKAMCSgsboWBfPs3c_vZR-lQ'
bot = telebot.TeleBot(token)

# Файл для хранения администратора
admin_file = 'admins.json'

# Загрузка администратора из файла
def load_admin():
    if os.path.exists(admin_file):
        with open(admin_file, 'r') as f:
            return set(json.load(f))
    return set()


# Сохранение администраторов в файл
def save_admin(admin):
    with open(admin_file, 'w') as f:
        json.dump(list(admin), f)


# Загрузка администраторов при старте бота
admin = load_admin()


@bot.message_handler(commands=['start', 'Старт'])
def start_message(message):
    user_id = message.from_user.id

    # Приветственное сообщение со списком команд
    welcome_text = (
        "Добро пожаловать! Вот список доступных команд:\n"
        "/start или /Старт - Приветственное сообщение\n"
        "/Удалить @username - Удалить пользователя из всех чатов\n"
    )

    # Проверяем, является ли пользователь администратором
    if user_id in admin:
        bot.send_message(message.chat.id, text=welcome_text + "Вы можете использовать команды бота.")
    else:
        # Проверяем, есть ли уже администратор
        if not admin:
            username = message.from_user.username or f"user_{user_id}"  # Используем ID, если нет юзернейма
            admin.add(user_id)  # Добавляем пользователя как администратора
            save_admin(admin)  # Сохраняем изменения
            bot.send_message(message.chat.id,
                             text=welcome_text + "Вы стали администратором. Чтобы удалить пользователя из всех чатов, введите команду /Удалить @<ник-пользователя>")
        else:
            bot.send_message(message.chat.id,
                             text=welcome_text + "У вас недостаточно прав. Только один пользователь может быть администратором.")

@bot.message_handler(commands=['get_chat_id'])
def send_chat_id(message):
    bot.send_message(message.chat.id, f"chat_id этой группы: {message.chat.id}")


@bot.message_handler(commands=['Удалить'])
def kick_user_by_id(message):
    # Получаем ID пользователя, которого нужно удалить
    user_name = message.text.split()[1]
    user = message.from_user.id
    cur.execute("SELECT chat_id, user_id FROM users WHERE username = %s;", (user_name,))


    # Получение результатов
    rows = cur.fetchall()
    for row in rows:
        chat_id, user_id = row
        member_status = bot.get_chat_member(chat_id, message.from_user.id).status

        if (member_status == 'administrator' or member_status == 'creator') and user in admin:
            try:
                bot.kick_chat_member(chat_id, user_id)
                bot.send_message(chat_id, f"Пользователь {user_name} был успешно удалён из чата.")
            except Exception as e:
                bot.send_message(chat_id,
                                 f"Не удалось удалить пользователя {user_name}. Возможно, у меня нет достаточных прав.")
    else:
            # Если пользователь не админ, отправляем сообщение об ошибке
        bot.send_message(message.from_user.id, "У вас недостаточно прав для выполнения этой команды в данном чате.")




@bot.message_handler(commands=['Администратор'])
def list_admins(message):
    if admin:
        admin_list = ', '.join(str(admin) for admin in admin)
        bot.send_message(message.chat.id, f"Текущий администратор: @{admin_list}")
    else:
        bot.send_message(message.chat.id, "Нет администраторов.")


bot.infinity_polling()