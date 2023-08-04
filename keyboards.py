import telebot

event_type_selection = telebot.types.ReplyKeyboardMarkup(True, True)
event_type_selection.row('Прогулка')
event_type_selection.row('Заезд')
event_type_selection.row('Гонка')

distance_selection = telebot.types.ReplyKeyboardMarkup(True, True)
distance_selection.row('30км','60км','>100км')
distance_selection.row('Назад')

walk_type_selection = telebot.types.ReplyKeyboardMarkup(True, True)
walk_type_selection.row('Для всех', 'Для девушек')
walk_type_selection.row('Назад')

see_more = telebot.types.ReplyKeyboardMarkup(True, True)
see_more.row('Выбрать другие события')

