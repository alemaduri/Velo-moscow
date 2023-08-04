# -*- coding: utf-8 -*-
import telebot  # ДЛЯ РАБОТЫ С API ТЕЛЕГРАМА
from threading import Thread  # ОБНОВЛЯТЬ БД БЕЗ ПРЕРЫВАНИЯ ОСНОВНОГО ЦИКЛА
import datetime
import time
import json  # ДЛЯ РАБОТЫ С БД
import keyboards  # КЛАВИАТУРЫ БОТА
import setup  # ГЛОБАЛЬНЫЕ КОНСТАНТЫ


def save_db():  # ФУНКЦИЯ СОХРАНЕНИЯ БД
    while True:
        time.sleep(10)
        dbjob = open(setup.DBPATH, 'w')
        dbjob.write(json.dumps(db, ensure_ascii=False, indent=4))
        dbjob.close()


def reply(message, text, keyboard = None, photo = False):
    if not photo:
        bot.send_message(message.chat.id, messages[text], reply_markup=keyboard)
    else:
        img = open(photo, 'rb')
        bot.send_photo(message.chat.id, img, messages[text], reply_markup=keyboard)


def reminder():
    while True:
        #  ОБНОВЛЯЕМ ПЕРЕМЕННУЮ С СОбыТИЯМИ КАЖДЫЙ ДЕНЬ
        events = json.load(open(setup.EVENTSPATH, 'r'))

        #  НАПОМИНАЕМ ПОЛЬЗОВАТЕЛЯМ О СОБЫТИЯХ
        now = datetime.datetime.today() + datetime.timedelta(days = 1)
        year = now.year
        month = now.month
        day = now.day
        for user in db.keys():
            if 'отслеживает' in db[user].keys():
                for event_name in db[user]['отслеживает']:
                    event = events[event_name]
                    event_date  = event['дата'].split('.')
                    event_date = list(map(int, event_date))
                    if day == event_date[0] and month == event_date[1] and year == event_date[2]:
                        bot.send_message(int(user), 'Уже завтра\nМероприятие ' + event["название"] + '\n' + event["ссылка"] + '\n\nНе пропустите!')

        time.sleep(86400) ##  ДОДЕЛАТЬ


def send_events(message):
    id = str(message.chat.id)
    req1 = db[id]["тип события"]
    if req1 == "гонка" or req1 == "заезд":
        req2 = db[id]["дистанция"]
    else:
        req2 = db[id]["тип прогулки"]
    sended = False
    for event in events.values():
        if event["тип"] == req1 and event["тип 2"] == req2:
            inline_button = telebot.types.InlineKeyboardButton('Отслеживать!', callback_data='A.'+event["название"])
            inline_kb = telebot.types.InlineKeyboardMarkup().add(inline_button)
            text = '<b>' + event["название"] + '</b>\n\n' + event["текст"] + '\n\n' + 'Дата: ' + event["дата"] + "\n" + event["ссылка"]
            image = open(event["изображение"], 'rb')
            #bot.send_message(message.chat.id, text, reply_markup=inline_kb, parse_mode='HTML')
            bot.send_photo(message.chat.id, image, text, parse_mode='HTML', reply_markup=inline_kb)
            sended = True
    if not sended:
        bot.send_message(message.chat.id, 'К сожалению, пока нет подходящих вам событий')



'''
# ОЧИСТКА БД ПЕРЕД КАЖДЫМ ЗАПУСКОМ, ЧТОБЫ ТЕСТИРОВАТЬ. ПОТОМ НАДО БУДЕТ УДАЛИТЬ
dbjob = open(setup.DBPATH, 'w')  # ПОТОМ УДАЛИТЬ
dbjob.write(json.dumps({}, ensure_ascii=False, indent=4))  # ПОТОМ УДАЛИТЬ
dbjob.close()  # ПОТОМ УДАЛИТЬ
'''
# ИНИЦИАЛИЗАЦИЯ БОТА
bot = telebot.TeleBot(setup.API_KEY)
# ИНИЦИАЛИЗАЦИЯ БД
db = json.load(open(setup.DBPATH, 'r'))
# ЗАГРУЗКА СООБЩЕНИЙ
messages = json.load(open(setup.MESSAGESPATH, 'r'))
# ЗАГРУЗКА СОБЫТИЙ
events = json.load(open(setup.EVENTSPATH, 'r'))
# КАЖДЫЕ 10 СЕКУНД В ОТДЕЛЬНОМ ПОТОКЕ СОХРАНЯЕМ БД 
# ЧТОБЫ В СЛУЧАЕМ ЕСЛИ БОТ НАКРОЕТСЯ НИЧЕГО НЕ ПОТЕРЯЛОСЬ
saving_db = Thread(target=save_db)
saving_db.start()
#Запускаем напоминалку
remind = Thread(target=reminder)
remind.start()


# ОТСЮДА НАЧИНАЕТСЯ ЛОГИКА БОТА

#ПРИВЕТСВеННОЕ СООбЩЕНИЕ
@bot.message_handler(commands=['start'])
def welcome_message(message):
    if str(message.chat.id) not in db.keys():
        reply(message, 'приветственное сообщение', keyboards.event_type_selection, 'contents/greetings.jpg')
        db[str(message.chat.id)] = {}
        db[str(message.chat.id)]["status"] = "тип"
    else:
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)
        db[str(message.chat.id)]["status"] = "тип"


@bot.message_handler(func=lambda message: db[str(message.chat.id)]["status"] == "тип")
def event_type_selection(message):
    if message.text.lower() == "гонка" or message.text.lower() == "заезд":
        db[str(message.chat.id)]["тип события"] = message.text.lower()
        db[str(message.chat.id)]["status"] = "выбор дистанции"
        reply(message, "выбор дистанции", keyboards.distance_selection)
    elif message.text.lower() == "прогулка":
        db[str(message.chat.id)]["тип события"] = message.text.lower()
        db[str(message.chat.id)]["status"] = "выбор типа прогулки"
        reply(message, "выбор типа прогулки", keyboards.walk_type_selection)
    else:
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)


@bot.message_handler(func=lambda message: db[str(message.chat.id)]["status"] == "выбор дистанции")
def distance_selection(message):
    if message.text == '30км':
        db[str(message.chat.id)]["дистанция"] = 30
    elif message.text == '60км':
        db[str(message.chat.id)]["дистанция"] = 60
    elif message.text == '>100км':
        db[str(message.chat.id)]["дистанция"] = 100
    elif message.text.lower() == 'назад':
        db[str(message.chat.id)]["status"] = "тип"
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)
        return 0
    else:
        reply(message, "выбор дистанции", keyboards.distance_selection)
        return 0
    db[str(message.chat.id)]["status"] = "конец"
    send_events(message)
    reply(message, "другие события", keyboards.see_more)


@bot.message_handler(func=lambda message: db[str(message.chat.id)]["status"] == "выбор типа прогулки")
def distance_selection(message):
    if message.text.lower() == 'для девушек':
        db[str(message.chat.id)]["тип прогулки"] = 'для девушек'
    elif message.text.lower() == 'для всех':
        db[str(message.chat.id)]["тип прогулки"] = 'для всех'
    elif message.text.lower() == 'назад':
        db[str(message.chat.id)]["status"] = "тип"
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)
        return 0
    else:
        reply(message, "выбор типа прогулки", keyboards.walk_type_selection)
        return 0
    db[str(message.chat.id)]["status"] = "конец"
    send_events(message)
    reply(message, "другие события", keyboards.see_more)


@bot.message_handler(func=lambda message: db[str(message.chat.id)]["status"] == "конец")
def end_selection(message):
    if message.text.lower() == "выбрать другие события":
        db[str(message.chat.id)]["status"] = "тип"
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)
    else:  # Тут можно не говорить что пользователь дурачок, а просто скинуть ему новый процесс выбора
        db[str(message.chat.id)]["status"] = "тип"
        reply(message, "приветственное сообщение 2", keyboards.event_type_selection)

@bot.callback_query_handler(func=lambda c: True)
def logic_inline(callback_query: telebot.types.CallbackQuery):
    text = callback_query.data
    if text.split('.')[0] == 'A':
        name = text.split('.')[1]
        if "отслеживает" in db[str(callback_query.from_user.id)].keys():
            if not name in db[str(callback_query.from_user.id)]["отслеживает"]:
                db[str(callback_query.from_user.id)]["отслеживает"].append(name)
                bot.answer_callback_query(callback_query.id, text='Вы отслеживаете ' + name)
            else:
                bot.answer_callback_query(callback_query.id, text='Вы уже отслеживаете ' + name)

        else:
            db[str(callback_query.from_user.id)]["отслеживает"] = [name]
            bot.answer_callback_query(callback_query.id, text='Вы отслеживаете ' + name)


# БЕСКОНЕЧНО ЖДЕМ НОВЫХ ДЕЙСТВИЕ ОТ ПОЛЬЗОВАТЕЛЯ
bot.infinity_polling(99999)
