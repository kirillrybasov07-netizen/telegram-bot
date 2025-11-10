import json
import os
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Прямое указание токена и ID (ЗАМЕНИТЕ НА ВАШИ!)
BOT_TOKEN = "8563201491:AAH_rDOPsbb10BL60duS6-K2tW0fLWb6gbg"
ADMIN_IDS = [895930863, 126013367, 1377287878]

# Файлы для хранения данных
SCHEDULE_FILE = "schedule.json"
HOMEWORK_FILE = "homework.json"

def load_data(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_data(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_main_keyboard(user_id):
    is_admin = user_id in ADMIN_IDS
    keyboard = [["📚 Посмотреть ДЗ", "📅 Посмотреть расписание"]]
    if is_admin:
        keyboard.append(["⚙️ Админ-панель"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        ["✏️ Изменить расписание", "📝 Изменить ДЗ"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_days_keyboard():
    keyboard = [
        ["📅 Понедельник", "📅 Вторник"],
        ["📅 Среда", "📅 Четверг"],
        ["📅 Пятница", "📅 Вся неделя"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def start(update, context):
    user_id = update.message.from_user.id
    text = "👋 Привет! Я бот для домашних заданий."
    if user_id in ADMIN_IDS:
        text += "\n⚙️ У вас есть доступ к админ-панели"
    update.message.reply_text(text, reply_markup=get_main_keyboard(user_id))

def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "📚 Посмотреть ДЗ":
        update.message.reply_text("Выберите день:", reply_markup=get_days_keyboard())
    elif text == "📅 Посмотреть расписание":
        schedule = load_data(SCHEDULE_FILE)
        if schedule:
            response = "📅 РАСПИСАНИЕ:\n\n"
            days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
            for day_num, day_name in days.items():
                response += f"{day_name}\n{schedule.get(day_num, 'Расписания нет')}\n\n"
            update.message.reply_text(response)
        else:
            update.message.reply_text("📅 Расписание еще не добавлено")
    elif text == "⚙️ Админ-панель" and user_id in ADMIN_IDS:
        update.message.reply_text("Админ-панель:", reply_markup=get_admin_keyboard())
    elif text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница"]:
        day_map = {"📅 Понедельник": "1", "📅 Вторник": "2", "📅 Среда": "3", "📅 Четверг": "4", "📅 Пятница": "5"}
        day_num = day_map[text]
        homework = load_data(HOMEWORK_FILE)
        day_names = {"1": "понедельник", "2": "вторник", "3": "среду", "4": "четверг", "5": "пятницу"}
        response = f"📚 ДЗ на {day_names[day_num]}:\n\n{homework.get(day_num, 'ДЗ не задано')}"
        update.message.reply_text(response, reply_markup=get_days_keyboard())
    elif text == "📅 Вся неделя":
        homework = load_data(HOMEWORK_FILE)
        if homework:
            response = "📚 ДЗ НА НЕДЕЛЮ:\n\n"
            days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
            for day_num, day_name in days.items():
                response += f"{day_name}\n{homework.get(day_num, 'ДЗ нет')}\n\n"
            update.message.reply_text(response, reply_markup=get_days_keyboard())
        else:
            update.message.reply_text("📚 Домашних заданий на неделю нет", reply_markup=get_days_keyboard())
    elif text == "🔙 Назад":
        update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(user_id))
    elif text == "✏️ Изменить расписание" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'schedule'
        update.message.reply_text("Введите расписание в формате:\n1: Математика 9:00\n2: Физика 10:00\n...")
    elif text == "📝 Изменить ДЗ" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'homework'
        update.message.reply_text("Введите ДЗ в формате:\n1: Учебник стр. 1-5\n2: Задачи стр. 10\n...")
    elif user_id in ADMIN_IDS and context.user_data.get('action'):
        action = context.user_data['action']
        data = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if parts[0].strip().isdigit():
                    data[parts[0].strip()] = parts[1].strip()
        if action == 'schedule':
            save_data(data, SCHEDULE_FILE)
            update.message.reply_text("✅ Расписание обновлено!", reply_markup=get_admin_keyboard())
        else:
            save_data(data, HOMEWORK_FILE)
            update.message.reply_text("✅ ДЗ обновлены!", reply_markup=get_admin_keyboard())
        context.user_data['action'] = None

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    logger.info("Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
