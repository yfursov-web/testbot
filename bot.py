import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Получаем токен из переменных окружения (Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Не найден TELEGRAM_TOKEN. Укажи его в настройках Render.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === БАЗА СЦЕНАРИЕВ (АДАПТИРОВАНО ДЛЯ МОБИЛЬНЫХ) ===
SCENARIOS = {
    "menu": {
        "text": "Привет, Управляющий! 🦅\nВыбери ситуацию для отработки:",
        # Замени ссылку ниже на свою ПРЯМУЮ ссылку (Raw)
        "photo": "https://drive.google.com/uc?export=view&id=1YC0O2inG1TMIadAw1aLWyd2-8Z89YQ5s",
        "buttons": [
            {"text": "🍕 Кейс 1: Бунт", "callback": "c1_start"},
            {"text": "🧹 Кейс 2: Бакаут", "callback": "c2_start"},
            {"text": "🏆 Кейс 3: Должность", "callback": "c3_start"},
            {"text": "🤝 Кейс 4: Передача смены", "callback": "c4_start"}
        ]
    },

    # -------- КЕЙС 1: БУНТ ИЗ-ЗА РЕВИЗИЙ --------
    "c1_start": {
        "text": "<b>Кейс 1: Ревизии</b>\nМенеджеры недовольны: «Либо я считаю, либо слежу за линией! Мы не успеваем!»\n\n<b>Твое действие:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+1:+Inventory+Revolt",
        "buttons": [
            {"text": "📅 Разобрать хронометраж", "callback": "c1_step2_good"},
            {"text": "⚠️ Это приказ", "callback": "c1_step2_bad"}
        ]
    },
    "c1_step2_good": {
        "text": "<b>Шаг 2: Встреча</b>\nКак начнешь разговор?\n\nВариант 1: «Я вижу, что нагрузка выросла, давайте искать решение.»\nВариант 2: «Почему вы считаете, что ревизия важнее линии?»",
        "buttons": [
            {"text": "1️⃣ Искать решение вместе", "callback": "c1_res_10"},
            {"text": "2️⃣ Задать жесткий вопрос", "callback": "c1_res_7"}
        ]
    },
    "c1_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\nМетод <b>Сотрудничества</b>. Услышал проблему, проявил эмпатию и вместе с командой нашел решение без потери стандартов.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c1_res_7": {
        "text": "📊 <b>Результат: 7/10</b>\nМетод <b>Соперничество</b>. Коммуникация была обвинительной. Стандарт будет внедрен, но лояльность команды упадет.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c1_step2_bad": {
        "text": "📊 <b>Результат: 4/10</b>\nЖесткое <b>Соперничество</b> без диалога. Стандарт выполнен, но в команде начнется скрытый бунт.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },

    # -------- КЕЙС 3: БИТВА ЗА ДОЛЖНОСТЬ --------
    "c3_start": {
        "text": "<b>Кейс 3: Заместитель</b>\nИрина и Сергей спорят при всех, кто станет замом. Команда раскололась.\n\n<b>Твой шаг:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+3:+Battle+for+Promotion",
        "buttons": [
            {"text": "🛑 Развести и провести 1:1", "callback": "c3_step2_good"},
            {"text": "🙈 Пусть сами решают", "callback": "c3_step2_bad"}
        ]
    },
    "c3_step2_good": {
        "text": "<b>Шаг 2: Решение</b>\nТы выслушал обоих. Как объявишь итог?\n\nВариант 1: «Выбрал Сергея, у него выше КЛН.»\nВариант 2: «Выбрал Ирину, она дольше работает.»",
        "buttons": [
            {"text": "1️⃣ По показателям КЛН", "callback": "c3_res_10"},
            {"text": "2️⃣ За стаж работы", "callback": "c3_res_6"}
        ]
    },
    "c3_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\n<b>Соперничество</b> в интересах бизнеса. Опора на прозрачные факты снимает неопределенность.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c3_res_6": {
        "text": "📊 <b>Результат: 6/10</b>\nВыбор по стажу демотивирует сильных сотрудников. Это выглядит как несправедливое отношение.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c3_step2_bad": {
        "text": "📊 <b>Результат: 2/10</b>\nМетод <b>Избегания</b>. Конфликт перерастет в кризис, работа пиццерии может встать.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },

    # -------- КЕЙС 4: НАСТЯ VS АНДРЕЙ --------
    "c4_start": {
        "text": "<b>Кейс 4: Передача смены</b>\nНастя злится на Андрея за грязные зоны. Андрея всё устраивает.\n\n<b>Твое действие:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+4:+Shift+Handover",
        "buttons": [
            {"text": "📋 Разобрать чек-лист", "callback": "c4_step2_good"},
            {"text": "🤐 Попросить Настю терпеть", "callback": "c4_res_bad"}
        ]
    },
    "c4_step2_good": {
        "text": "<b>Шаг 2: Встреча</b>\nКак построишь диалог?\n\nВариант 1: «Андрей, посмотри на фото, это не стандарт.»\nВариант 2: «Давайте вместе решим, какой результат нужен.»",
        "buttons": [
            {"text": "2️⃣ Решать вместе", "callback": "c4_res_10"},
            {"text": "1️⃣ Указать на ошибки", "callback": "c4_res_7"}
        ]
    },
    "c4_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\n<b>Сотрудничество</b>. Ты помог договориться и достичь общей цели. План зафиксирован.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c4_res_7": {
        "text": "📊 <b>Результат: 7/10</b>\nТы не вовлек Андрея в поиск решения. Он может воспринять это как давление.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c4_res_bad": {
        "text": "📊 <b>Результат: 3/10</b>\n<b>Уступка</b> нарушителю. Настя почувствует несправедливость и может уйти.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    
    # -------- КЕЙС 2: БАКАУТ --------
    "c2_start": {
        "text": "<b>Кейс 2: Полы</b>\nКурьер отказывается мыть полы: «Я устал, пусть стажеры моют!»\n\n<b>Твой выбор:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+2:+Dirty+Floors",
        "buttons": [
            {"text": "🤝 «Помогу тебе, закончим»", "callback": "c2_res_10"},
            {"text": "😠 «Мой или штраф»", "callback": "c2_res_6"}
        ]
    },
    "c2_res_10": {"text": "📊 <b>10/10.</b> Сотрудничество и лидерство на примере.", "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]},
    "c2_res_6": {"text": "📊 <b>6/10.</b> Соперничество. Стандарт выполнен, но контакт ослаб.", "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]}
}

# === ОБРАБОТЧИКИ ТЕЛЕГРАМ ===

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_node(message.chat.id, "menu")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Убираем "часики" загрузки на кнопке
    bot.answer_callback_query(call.id)
    
    # Удаляем предыдущее сообщение, чтобы чат выглядел как аккуратный квест
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
        
    send_node(call.message.chat.id, call.data)

def send_node(chat_id, node_id):
    if node_id not in SCENARIOS:
        return
        
    node = SCENARIOS[node_id]
    text = node["text"]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for btn in node.get("buttons", []):
        markup.add(types.InlineKeyboardButton(btn["text"], callback_data=btn["callback"]))
        
    # Бронебойная логика отправки сообщений
    if "photo" in node:
        try:
            # Пытаемся отправить с картинкой
            bot.send_photo(chat_id, node["photo"], caption=text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            print(f"Ошибка загрузки фото: {e}")
            # Если Телеграм забраковал ссылку на фото, отправляем просто текст
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    else:
        # Если картинки в сценарии нет, отправляем просто текст
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === МИКРО-СЕРВЕР ДЛЯ ХОСТИНГА НА RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Интерактивный тренажер Додо работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("Запуск веб-сервера...")
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    print("Сбрасываем старые вебхуки...")
    bot.remove_webhook()
    
    print("Кнопочный бот-тренажер запущен...")
    bot.polling(none_stop=True)
