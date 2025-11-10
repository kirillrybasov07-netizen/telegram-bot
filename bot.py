import json
import os
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get('8563201491:AAH_rDOPsbb10BL60duS6-K2tW0fLWb6gbg')
ADMIN_IDS = eval(os.environ.get('ADMIN_IDS', '[895930863, 1377287878, 1260133367]'))

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

# Файлы для хранения данных
SCHEDULE_FILE = "schedule.json"
HOMEWORK_FILE = "homework.json"

def load_data(filename):
    """Загрузка данных из JSON файла"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
    return {}

def save_data(data, filename):
    """Сохранение данных в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

# Клавиатуры
def get_main_keyboard(user_id):
    """Основная клавиатура"""
    is_admin = user_id in ADMIN_IDS
    keyboard = [
        [KeyboardButton("📚 Посмотреть ДЗ"), KeyboardButton("📅 Посмотреть расписание")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton("⚙️ Админ-панель")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Клавиатура админ-панели"""
    keyboard = [
        ["✏️ Изменить расписание", "📝 Изменить ДЗ"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_days_keyboard():
    """Клавиатура выбора дней"""
    keyboard = [
        ["📅 Понедельник", "📅 Вторник"],
        ["📅 Среда", "📅 Четверг"],
        ["📅 Пятница", "📅 Вся неделя"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команды бота
def start(update, context):
    """Обработчик команды /start"""
    user_id = update.message.from_user.id
    welcome_text = "👋 Привет! Я бот для домашних заданий.\n\n📚 Посмотреть ДЗ - посмотреть домашние задания\n📅 Посмотреть расписание - посмотреть расписание занятий"
    
    if user_id in ADMIN_IDS:
        welcome_text += "\n\n⚙️ У вас есть доступ к админ-панели"
    
    update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(user_id))

def handle_message(update, context):
    """Обработчик текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "📚 Посмотреть ДЗ":
        update.message.reply_text("Выберите день:", reply_markup=get_days_keyboard())
    
    elif text == "📅 Посмотреть расписание":
        show_schedule(update, user_id)
    
    elif text == "⚙️ Админ-панель" and user_id in ADMIN_IDS:
        update.message.reply_text("Админ-панель:", reply_markup=get_admin_keyboard())
    
    elif text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница"]:
        show_homework_for_day(update, text, user_id)
    
    elif text == "📅 Вся неделя":
        show_all_homework(update, user_id)
    
    elif text == "🔙 Назад":
        update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(user_id))
    
    # Админские функции
    elif text == "✏️ Изменить расписание" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'waiting_schedule'
        update.message.reply_text(
            "Введите новое расписание. Каждая строка - день недели:\n"
            "1: Математика 9:00, Физика 11:00\n"
            "2: Литература 9:00, Химия 11:00\n"
            "3: История 9:00, Биология 11:00\n"
            "4: Английский 9:00, Физра 11:00\n"
            "5: Информатика 9:00, География 11:00\n\n"
            "Отправьте одним сообщением:"
        )
    
    elif text == "📝 Изменить ДЗ" and user_id in ADMIN_IDS:
        context.user_data['action'] = 'waiting_homework'
        update.message.reply_text(
            "Введите ДЗ. Каждая строка - день недели:\n"
            "1: Учебник стр. 45-50, упр. 1-5\n"
            "2: Подготовить доклад\n"
            "3: Решить задачи по физике\n"
            "4: Сочинение на тему 'Лето'\n"
            "5: Проект по информатике\n\n"
            "Отправьте одним сообщением:"
        )
    
    # Обработка ввода от админа
    elif user_id in ADMIN_IDS and context.user_data.get('action'):
        handle_admin_input(update, context, text, user_id)

def show_schedule(update, user_id):
    """Показать расписание"""
    schedule = load_data(SCHEDULE_FILE)
    if not schedule:
        update.message.reply_text("📅 Расписание еще не добавлено", 
                                reply_markup=get_main_keyboard(user_id))
        return
    
    schedule_text = "📅 РАСПИСАНИЕ:\n\n"
    days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
    
    for day_num, day_name in days.items():
        schedule_text += f"{day_name}\n"
        if day_num in schedule:
            schedule_text += f"{schedule[day_num]}\n"
        else:
            schedule_text += "Расписания нет\n"
        schedule_text += "\n"
    
    update.message.reply_text(schedule_text, reply_markup=get_main_keyboard(user_id))

def show_homework_for_day(update, day_button, user_id):
    """Показать ДЗ для конкретного дня"""
    day_mapping = {
        "📅 Понедельник": "1",
        "📅 Вторник": "2", 
        "📅 Среда": "3",
        "📅 Четверг": "4",
        "📅 Пятница": "5"
    }
    
    day_num = day_mapping.get(day_button)
    homework = load_data(HOMEWORK_FILE)
    
    day_names = {"1": "понедельник", "2": "вторник", "3": "среду", 
                 "4": "четверг", "5": "пятницу"}
    
    if day_num in homework:
        response = f"📚 ДЗ на {day_names[day_num]}:\n\n{homework[day_num]}"
    else:
        response = f"📚 На {day_names[day_num]} домашнее задание не задано"
    
    update.message.reply_text(response, reply_markup=get_days_keyboard())

def show_all_homework(update, user_id):
    """Показать все ДЗ на неделю"""
    homework = load_data(HOMEWORK_FILE)
    if not homework:
        update.message.reply_text("📚 Домашних заданий на неделю нет", 
                                reply_markup=get_days_keyboard())
        return
    
    hw_text = "📚 ДЗ НА НЕДЕЛЮ:\n\n"
    days = {"1": "ПОНЕДЕЛЬНИК", "2": "ВТОРНИК", "3": "СРЕДА", 
            "4": "ЧЕТВЕРГ", "5": "ПЯТНИЦА"}
    
    for day_num, day_name in days.items():
        hw_text += f"{day_name}\n"
        if day_num in homework:
            hw_text += f"{homework[day_num]}\n"
        else:
            hw_text += "ДЗ нет\n"
        hw_text += "\n"
    
    update.message.reply_text(hw_text, reply_markup=get_days_keyboard())

def handle_admin_input(update, context, text, user_id):
    """Обработка ввода от администратора"""
    action = context.user_data.get('action')
    
    if action == 'waiting_schedule':
        # Парсинг расписания
        schedule = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line and line.split(':')[0].strip().isdigit():
                day_num = line.split(':')[0].strip()
                day_schedule = line.split(':', 1)[1].strip()
                schedule[day_num] = day_schedule
        
        if save_data(schedule, SCHEDULE_FILE):
            update.message.reply_text("✅ Расписание обновлено!", 
                                    reply_markup=get_admin_keyboard())
        else:
            update.message.reply_text("❌ Ошибка сохранения расписания", 
                                    reply_markup=get_admin_keyboard())
        context.user_data['action'] = None
    
    elif action == 'waiting_homework':
        # Парсинг ДЗ
        homework = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line and line.split(':')[0].strip().isdigit():
                day_num = line.split(':')[0].strip()
                day_homework = line.split(':', 1)[1].strip()
                homework[day_num] = day_homework
        
        if save_data(homework, HOMEWORK_FILE):
            update.message.reply_text("✅ Домашние задания обновлены!", 
                                    reply_markup=get_admin_keyboard())
        else:
            update.message.reply_text("❌ Ошибка сохранения ДЗ", 
                                    reply_markup=get_admin_keyboard())
        context.user_data['action'] = None

def error_handler(update, context):
    """Обработчик ошибок"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Основная функция"""
    logger.info("Starting bot...")
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error_handler)
    
    logger.info("Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
