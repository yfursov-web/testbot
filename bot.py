import os
import telebot
from telebot import types
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Загрузка переменных окружения из файла .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Словарь для хранения сессий пользователей (контекст диалога)
user_sessions = {}

# === БАЗА СЦЕНАРИЕВ ===
SCENARIOS = {
    "case_1": {
        "title": "🍕 Кейс 1: Настя против Андрея (Межличностный)",
        "description": "Менеджер Настя жалуется, что Андрей плохо передает смену и оставляет грязь. Твоя задача — выступить 3-й стороной и решить конфликт.",
        "system_prompt": """Ты — менеджер Андрей в Додо Пицце. Настя постоянно придирается к тебе из-за чистоты при передаче смены. 
        Ты считаешь, что делаешь всё нормально, а у неё завышенные требования. 
        Ты раздражен. Твоя стартовая позиция: 'Я всё делаю по чеклисту, мне некогда за каждым пятном бегать'.
        Отвечай Управляющему (пользователю) коротко, эмоционально. Не сдавайся сразу, проверь Управляющего на эмпатию и умение договариваться."""
    },
    "case_2": {
        "title": "⚡️ Кейс 2: Бунт из-за ревизий",
        "description": "Ты ввел ежедневные ревизии. Опытный менеджер злится, что из-за этого не успевает делать другие задачи.",
        "system_prompt": """Ты — опытный менеджер смены в Додо Пицце. Управляющий (пользователь) ввел новые ежедневные ревизии.
        Ты злишься, потому что это отнимает время от других задач на смене (линия, заказы).
        Твоя позиция: 'Либо я считаю остатки, либо я слежу за линией. Я не робот!'
        Отвечай Управляющему дерзко, но в рамках корпоративной этики. Уступи только если Управляющий применит метод 'соперничества' (твердость ради результата) или предложит логичный компромисс."""
    },
    "case_3": {
        "title": "🌴 Кейс 3: Внеплановый отпуск",
        "description": "Отличный менеджер требует внеплановый отпуск, угрожая увольнением. Графики уже утверждены.",
        "system_prompt": """Ты — один из лучших менеджеров пиццерии. Тебе срочно нужен внеплановый отпуск по личным обстоятельствам.
        Управляющий (пользователь) отказывает, так как графики согласованы.
        Твоя позиция: 'Я всё понимаю про график, но мне правда нужно уехать. Если не договоримся — пишите заявление по собственному'.
        Твоя цель: получить отпуск. Ты готов уйти, если Управляющий выберет 'достижение цели' (отказ), а не 'сохранение отношений' (уступка)."""
    }
}

# Промпт для оценки (Асессор)
ASSESSOR_PROMPT = """Ты — эксперт-тренажер 'Додо Пицца'. Твоя задача — оценить диалог между Управляющим (User) и сотрудником (Assistant) по решению конфликта.
Оцени действия Управляющего по 10-балльной шкале, учитывая:
1. Эмпатия (услышал ли эмоции и факты).
2. Выбор метода (соперничество, сотрудничество, компромисс, уступка, избегание). Правильно ли выбран метод для конкретной ситуации?
3. Сохранение авторитета и стандартов компании.
Выдай структурированный и краткий фидбек: что получилось хорошо, а что стоит улучшить."""

# === ЛОГИКА БОТА ===

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(SCENARIOS["case_1"]["title"], callback_data="case_1")
    btn2 = types.InlineKeyboardButton(SCENARIOS["case_2"]["title"], callback_data="case_2")
    btn3 = types.InlineKeyboardButton(SCENARIOS["case_3"]["title"], callback_data="case_3")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id, 
        "Привет, Управляющий! 🦅 Готов проверить свои навыки решения конфликтов?\n\nВыбери сценарий:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in SCENARIOS)
def start_scenario(call):
    chat_id = call.message.chat.id
    scenario_id = call.data
    scenario = SCENARIOS[scenario_id]
    
    # Инициализация сессии
    user_sessions[chat_id] = {
        "status": "in_progress",
        "messages": [
            {"role": "system", "content": scenario["system_prompt"]}
        ]
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🛑 Завершить диалог и получить оценку"))
    
    bot.send_message(
        chat_id, 
        f"*{scenario['title']}*\n_{scenario['description']}_\n\nДиалог начат. Напиши свое первое сообщение сотруднику:", 
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🛑 Завершить диалог и получить оценку")
def end_scenario_and_evaluate(message):
    chat_id = message.chat.id
    
    if chat_id not in user_sessions or user_sessions[chat_id]["status"] != "in_progress":
        bot.send_message(chat_id, "Нет активного диалога. Нажми /start", reply_markup=types.ReplyKeyboardRemove())
        return

    bot.send_message(chat_id, "⏳ Анализирую твои действия как Управляющего...", reply_markup=types.ReplyKeyboardRemove())
    
    # Меняем системный промпт на Асессора, передавая всю историю
    history = user_sessions[chat_id]["messages"]
    evaluation_messages = [{"role": "system", "content": ASSESSOR_PROMPT}] + history
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=evaluation_messages,
            temperature=0.7
        )
        feedback = response.choices[0].message.content
        bot.send_message(chat_id, f"📊 **Результат разбора:**\n\n{feedback}", parse_mode="Markdown")
        
        # Очищаем сессию
        user_sessions[chat_id]["status"] = "finished"
        bot.send_message(chat_id, "Чтобы начать новый кейс, жми /start")
        
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при обращении к ИИ: {e}")

@bot.message_handler(func=lambda message: True)
def handle_conversation(message):
    chat_id = message.chat.id
    
    if chat_id not in user_sessions or user_sessions[chat_id]["status"] != "in_progress":
        bot.send_message(chat_id, "Пожалуйста, выбери кейс через команду /start")
        return

    # Добавляем реплику Управляющего в историю
    user_sessions[chat_id]["messages"].append({"role": "user", "content": message.text})
    
    bot.send_chat_action(chat_id, 'typing')
    
    try:
        # Запрашиваем ответ у нейросети (сотрудника)
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=user_sessions[chat_id]["messages"],
            temperature=0.8,
            max_tokens=300
        )
        
        bot_reply = response.choices[0].message.content
        
        # Сохраняем ответ бота в историю
        user_sessions[chat_id]["messages"].append({"role": "assistant", "content": bot_reply})
        
        bot.send_message(chat_id, bot_reply)
        
    except Exception as e:
        bot.send_message(chat_id, f"Сотрудник ушел в себя (ошибка API): {e}")

# Запуск бота
# === МИКРО-СЕРВЕР ДЛЯ ХОСТИНГА ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Тренажер Додо Пиццы работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("Запуск веб-сервера...")
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    print("Бот-тренажер для Управляющих запущен...")
    bot.polling(none_stop=True)
