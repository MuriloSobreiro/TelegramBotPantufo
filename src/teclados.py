import telebot


def rolagemDados() -> telebot.types.ReplyKeyboardMarkup():
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row_width = 4
    keyboard.add("/r moeda", "/r fechar")
    for d in ["4", "6", "8", "10", "12", "20"]:
        keyboard.add("/r 1d" + d, "/r 2d" + d, "/r 3d" + d, "/r 4d" + d)
    return keyboard


def itemTags(lista: list) -> telebot.types.ReplyKeyboardMarkup():
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for l in lista:
        keyboard.add(l)
    return keyboard
