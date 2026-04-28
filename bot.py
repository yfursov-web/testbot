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

# === БАЗА СЦЕНАРИЕВ С ФОТО И HTML-РАЗМЕТКОЙ ===
SCENARIOS = {
    "menu": {
        "text": "Привет, Управляющий! 🦅\nВыбери ситуацию для тренировки:",
        "photo": "https://drive.google.com/file/d/1YC0O2inG1TMIadAw1aLWyd2-8Z89YQ5s/view?usp=sharing"
        "buttons": [
            {"text": "🍕 Кейс 1: Бунт из-за ревизий", "callback": "c1_start"},
            {"text": "🧹 Кейс 2: Грязный бакаут", "callback": "c2_start"},
            {"text": "🏆 Кейс 3: Битва за должность", "callback": "c3_start"},
            {"text": "🤝 Кейс 4: Настя vs Андрей", "callback": "c4_start"}
        ]
    },

    # -------- КЕЙС 1: БУНТ ИЗ-ЗА РЕВИЗИЙ --------
    "c1_start": {
        "text": "<b>Кейс 1: Ревизии</b>\nМенеджеры недовольны ежедневными ревизиями: «Либо я считаю, либо слежу за линией! Мы не успеваем!»\n\n<b>Твое первое действие:</b>",
        "photo": "https://drive.google.com/file/d/1JqInvSoqkF6ptHFo0O12UfVYf9HTzxEX/view?usp=sharing",
        "buttons": [
            {"text": "Назначить встречу и разобрать хронометраж", "callback": "c1_step2_good"},
            {"text": "Сказать, что это приказ и обсуждению не подлежит", "callback": "c1_step2_bad"}
        ]
    },
    "c1_step2_good": {
        "text": "<b>Шаг 2: Коммуникация</b>\nТы решил разобраться в причинах. Как начнешь разговор на встрече?",
        "buttons": [
            {"text": "«Я вижу, что нагрузка выросла, давайте поищем решение.»", "callback": "c1_res_10"},
            {"text": "«Почему вы считаете, что ревизия важнее линии?»", "callback": "c1_res_7"}
        ]
    },
    "c1_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\nТы применил метод <b>Сотрудничества</b>. Услышал проблему, проявил эмпатию и вместе с командой нашел решение без потери стандартов.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c1_res_7": {
        "text": "📊 <b>Результат: 7/10</b>\nТы сфокусировался на фактах, но коммуникация была обвинительной. Метод <b>Соперничество</b> поможет внедрить стандарт, но лояльность команды может снизиться.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c1_step2_bad": {
        "text": "📊 <b>Результат: 4/10</b>\nТы выбрал жесткое <b>Соперничество</b> без диалога. В Додо важно создавать доверительную атмосферу. Стандарт будет выполнен, но в команде начнется скрытый бунт.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },

    # -------- КЕЙС 3: БИТВА ЗА ДОЛЖНОСТЬ --------
    "c3_start": {
        "text": "<b>Кейс 3: Выбор заместителя</b>\nИрина и Сергей публично спорят, кто должен стать твоим замом. Атмосфера накалена, сотрудники делятся на два лагеря.\n\n<b>Твой первый шаг:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+3:+Battle+for+Promotion",
        "buttons": [
            {"text": "Пусть сами договорятся между собой", "callback": "c3_step2_bad"},
            {"text": "Развести их и назначить встречи 1:1", "callback": "c3_step2_good"}
        ]
    },
    "c3_step2_good": {
        "text": "<b>Шаг 2: Оценка и решение</b>\nТы выслушал обоих. Как объявишь решение?",
        "buttons": [
            {"text": "«Я выбрал Сергея, так как у него выше КЛН.»", "callback": "c3_res_10"},
            {"text": "«Я выбрал Ирину, потому что она дольше работает.»", "callback": "c3_res_6"}
        ]
    },
    "c3_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\nТы применил <b>Соперничество</b> в интересах пиццерии. Опирался на прозрачные факты и показатели эффективности, что снимает неопределенность.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c3_res_6": {
        "text": "📊 <b>Результат: 6/10</b>\nВыбор по стажу, а не по эффективности, может выглядеть как несправедливое отношение. Это демотивирует сильных сотрудников.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c3_step2_bad": {
        "text": "📊 <b>Результат: 2/10</b>\nМетод <b>Избегания</b> губителен. Конфликт перерастет в кризис, а работа пиццерии может встать из-за ошибок.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },

    # -------- КЕЙС 4: НАСТЯ VS АНДРЕЙ --------
    "c4_start": {
        "text": "<b>Кейс 4: Передача смены</b>\nНастя злится на Андрея за грязные зоны. Андрей считает, что его работа его устраивает.\n\n<b>Как поступишь?</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+4:+Shift+Handover",
        "buttons": [
            {"text": "Провести общую встречу и разобрать чек-лист", "callback": "c4_step2_good"},
            {"text": "Сказать Насте, чтобы она была терпимее", "callback": "c4_res_bad"}
        ]
    },
    "c4_step2_good": {
        "text": "<b>Шаг 2: Коммуникация на встрече</b>\nКак построишь диалог?",
        "buttons": [
            {"text": "«Андрей, посмотри на фото, это не стандарт.»", "callback": "c4_res_7"},
            {"text": "«Давайте вместе решим, какой результат мы хотим видеть.»", "callback": "c4_res_10"}
        ]
    },
    "c4_res_10": {
        "text": "📊 <b>Результат: 10/10</b>\nМетод <b>Сотрудничества</b>. Ты помог сторонам договориться и достичь общей цели. План зафиксирован.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c4_res_7": {
        "text": "📊 <b>Результат: 7/10</b>\nТы опирался на факты, но не вовлек Андрея в поиск решения. Он может воспринять это как давление.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    "c4_res_bad": {
        "text": "📊 <b>Результат: 3/10</b>\nЭто <b>Уступка</b> нарушителю. Настя почувствует несправедливость и может уволиться.",
        "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]
    },
    
    # -------- КЕЙС 2: БАКАУТ --------
    "c2_start": {
        "text": "<b>Кейс 2: Полы</b>\nКурьер отказывается мыть полы: «Я устал, пусть стажеры моют!»\n\n<b>Твой выбор:</b>",
        "photo": "https://placehold.co/800x400/222222/FF6900?text=Case+2:+Dirty+Floors",
        "buttons": [
            {"text": "«Я помогу тебе, закончим быстрее.»", "callback": "c2_res_10"},
            {"text": "«Это твоя обязанность, мой или штраф.»", "callback": "c2_res_6"}
        ]
    },
    "c2_res_10": {"text": "📊 <b>10/10.</b> Сотрудничество и лидерство на примере.", "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]},
    "c2_res_6": {"text": "📊 <b>6/10.</b> Соперничество. Стандарт выполнен, но контакт с командой ослаб.", "buttons": [{"text": "⬅️ В меню", "callback": "menu"}]}
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
        
    # Если в узле есть картинка, отправляем фото с подписью
    if "photo" in node:
        bot.send_photo(chat_id, node["photo"], caption=text, parse_mode="HTML", reply_markup=markup)
    else:
        # Если картинки нет, отправляем просто текст
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === МИКРО-СЕРВЕР ДЛЯ ХОСТИНГА НА RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Интерактивный тренажер Додо работает чисто и с картинками!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    print("Запуск веб-сервера...")
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    print("Кнопочный бот-тренажер запущен...")
    bot.polling(none_stop=True)
