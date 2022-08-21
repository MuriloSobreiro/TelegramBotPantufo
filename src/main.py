import os
import re
import telebot
from dotenv import load_dotenv

import termooo
import rpg

load_dotenv()
bot = telebot.TeleBot(os.environ["BOT_AUTH"])


"""
Features:
Calculadora de Term.ooo
Rolagem de dados


"""
@bot.message_handler(commands=["rolar","rola","roll"])
def rolarDados(menssagem):
    dados = re.findall(r"\d+d\d+", menssagem.text)
    if dados:
        res = rpg.rolarDados(dados[0])
        bot.reply_to(menssagem,res)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()

        for d in ['4','6','8','10','12','20']:
            keyboard.add(telebot.types.InlineKeyboardButton('1d'+d, callback_data='rolar 1d'+d))

        bot.send_message(menssagem.chat.id, text='Escolha a rolagem', reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("rolar"):
        bot.answer_callback_query(call.id, rpg.rolarDados(call.data.replace("rolar ",'')))

def termooVerify(menssagem):
    texto = menssagem.text
    return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")

@bot.message_handler(func=termooVerify)
def termoo(mensssagem):
    res = termooo.registrar(mensssagem.text, mensssagem.from_user.first_name + " " + mensssagem.from_user.last_name)
    bot.send_message(mensssagem.chat.id,"Registro: " + str(res))

def verificar(menssagem):
    return True

@bot.message_handler(func=verificar)
def responder(menssagem):
    print(menssagem)
    res ="""
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /rolar para jogar dados
    """
    bot.reply_to(menssagem,res)

bot.polling()