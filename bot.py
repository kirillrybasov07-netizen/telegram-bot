import json
import os
import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# НАСТРОЙКИ - ЗАМЕНИТЕ ЭТО!
BOT_TOKEN = "8563201491:AAH_rDOPsbb10BL60duS6-K2tW0fLWb6gbg"
ADMIN_IDS = [895930863, 1377287878, 1260133367]  # Ваш цифровой ID из Telegram

# Загрузка данных
def load_schedule():
    if os.path.exists("schedule.json"):
        with open("schedule.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_schedule(data):
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_homework():
    if os.path.exists("homework.json"):
        with open("homework.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_homework(data):
    with open("homework.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Клавиатуры
def get_main_keyboard(user_id):
    is_admin = user_id in ADMIN_IDS
    keyboard = [
        ["📚 Посмотреть ДЗ", "📅 Посмотреть расписание"]
    ]
    if is_admin:
        keyboard.append(["⚙️ Админ-панель"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_days_keyboard():
    keyboard = [
        ["📅 Понедельник", "📅 Вторник", "📅 Среда"],
        ["📅 Четверг", "📅 Пятница", "📅 Вся неделя"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        ["✏️ Изменить расписание", "📝 Изменить ДЗ"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команды бота
def start(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text(
        "👋 Привет! Я бот для домашних заданий.\n\n"
        "📚 - Посмотреть домашнее задание\n"
        "📅 - Посмотреть расписание\n"
        "⚙️ - Админ-панель (только для админов)",
        reply_markup=get_main_keyboard(user_id)
    )

def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "📚 Посмотреть ДЗ":
        update.message.reply_text("Выберите день:", reply_markup=get_days_keyboard())
    
    elif text == "📅 Посмотреть расписание":
        schedule = load_schedule()
        if schedule:
            response = "📅 РАСПИСАНИЕ:\n\n"
            days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
            for day_num, day_name in days.items():
                response += f"**{day_name}**\n"
                if day_num in schedule:
                    response += f"{schedule[day_num]}\n"
                else:
                    response += "Расписания нет\n"
                response += "\n"
            update.message.reply_text(response, reply_markup=get_main_keyboard(user_id))
        else:
            update.message.reply_text("📅 Расписание еще не добавлено", reply_markup=get_main_keyboard(user_id))
    
    elif text == "⚙️ Админ-панель" and user_id in ADMIN_IDS:
        update.message.reply_text("Админ-панель:", reply_markup=get_admin_keyboard())
    
    # Просмотр ДЗ по дням
    elif text == "📅 Понедельник":
        show_homework(update, "1", "понедельник", user_id)
    elif text == "📅 Вторник":
        show_homework(update, "2", "вторник", user_id)
    elif text == "📅 Среда":
        show_homework(update, "3", "среду", user_id)
    elif text == "📅 Четверг":
        show_homework(update, "4", "четверг", user_id)
    elif text == "📅 Пятница":
        show_homework(update, "5", "пятницу", user_id)
    
    elif text == "📅 Вся неделя":
        homework = load_homework()
        if homework:
            response = "📚 ДЗ НА НЕДЕЛЮ:\n\n"
            days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
            for day_num, day_name in days.items():
                response += f"**{day_name}**\n"
                if day_num in homework:
                    response += f"{homework[day_num]}\n"
                else:
                    response += "ДЗ нет\n"
                response += "\n"
            update.message.reply_text(response, reply_markup=get_days_keyboard())
        else:
            update.message.reply_text("📚 Домашних заданий на неделю нет", reply_markup=get_days_keyboard())
    
    # Админские функции
    elif text == "✏️ Изменить расписание" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'waiting_schedule'
        update.message.reply_text(
            "Введите расписание в формате:\n"
            "1: Математика 9:00-10:30, Физика 11:00-12:30\n"
            "2: Литература 9:00-10:30, Химия 11:00-12:30\n"
            "и т.д. (1-понедельник, 2-вторник...)\n\n"
            "Отправьте одним сообщением:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Отмена"]], resize_keyboard=True)
        )
    
    elif text == "📝 Изменить ДЗ" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'waiting_homework'
        update.message.reply_text(
            "Введите ДЗ в формате:\n"
            "1: Стр. 25-30, упр. 5-10\n"
            "2: Подготовить доклад\n"
            "и т.д. (1-понедельник, 2-вторник...)\n\n"
            "Отправьте одним сообщением:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Отмена"]], resize_keyboard=True)
        )
    
    elif text == "🔙 Назад":
        update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(user_id))
    
    elif text == "🔙 Отмена":
        context.user_data['action'] = None
        update.message.reply_text("Отменено", reply_markup=get_admin_keyboard() if user_id in ADMIN_IDS else get_main_keyboard(user_id))
    
    # Обработка ввода расписания/ДЗ от админа
    elif user_id in ADMIN_IDS and 'action' in context.user_data:
        handle_admin_input(update, context, text, user_id)

def show_homework(update, day_num, day_name, user_id):
    homework = load_homework()
    if day_num in homework:
        response = f"📚 ДЗ на {day_name}:\n\n{homework[day_num]}"
    else:
        response = f"📚 На {day_name} домашнее задание не задано"
    update.message.reply_text(response, reply_markup=get_days_keyboard())

def handle_admin_input(update, context, text, user_id):
    action = context.user_data.get('action')
    
    if action == 'waiting_schedule':
        # Простой парсинг расписания
        schedule = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                day_num = line.split(':')[0].strip()
                day_schedule = line.split(':', 1)[1].strip()
                schedule[day_num] = day_schedule
        
        save_schedule(schedule)
        update.message.reply_text("✅ Расписание обновлено!", reply_markup=get_admin_keyboard())
        context.user_data['action'] = None
    
    elif action == 'waiting_homework':
        # Простой парсинг ДЗ
        homework = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                day_num = line.split(':')[0].strip()
                day_homework = line.split(':', 1)[1].strip()
                homework[day_num] = day_homework
        
        save_homework(homework)
        update.message.reply_text("✅ Домашние задания обновлены!", reply_markup=get_admin_keyboard())
        context.user_data['action'] = None

# Запуск бота
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    print("✅ Бот запущен! Ищите его в Telegram")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
