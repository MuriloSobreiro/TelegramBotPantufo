import os
import re
import telebot
from dotenv import load_dotenv

import termooo
import rpg

load_dotenv()
bot = telebot.TeleBot(os.environ["BOT_AUTH"])
print("Bot iniciado")

"""
Features:
Calculadora de Term.ooo
Rolagem de dados


"""
@bot.message_handler(commands=["rolar","rola","roll","r"])
def rolarDados(menssagem):
    dados = re.findall(r"\d+d\d+", menssagem.text)
    if dados:
        res = rpg.rolarDados(dados[0])
        bot.reply_to(menssagem,res)
    else:
        if menssagem.text.endswith("fechar"):
            bot.send_message(menssagem.chat.id, text='Fechando rolagem', reply_markup=telebot.types.ReplyKeyboardRemove())
            return
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row_width = 4
        keyboard.add("/r fechar")
        for d in ['4','6','8','10','12','20']:
             keyboard.add('/r 1d'+d,'/r 2d'+d,'/r 3d'+d,'/r 4d'+d)
        bot.send_message(menssagem.chat.id, text='Escolha a rolagem', reply_markup=keyboard)
    print("Rolagem de dados: " + menssagem.text)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("rolar"):
        bot.answer_callback_query(call.id, rpg.rolarDados(call.data.replace("rolar ",'')))

def termooVerify(menssagem):
    texto = menssagem.text
    return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")

@bot.message_handler(func=termooVerify)
def termoo(mensssagem):
    print(mensssagem)
    if mensssagem.from_user.last_name:
        nome = mensssagem.from_user.first_name + " " + mensssagem.from_user.last_name
    elif mensssagem.from_user.username:
        nome = mensssagem.from_user.username
    else:
        nome = mensssagem.from_user.first_name
    res = termooo.registrar(mensssagem.text, nome, mensssagem.from_user.id)
    bot.send_message(mensssagem.chat.id,"Registro: " + str(res))
    print("Registro de Termooo")

def verificar(menssagem):
    return True

@bot.message_handler(func=verificar)
def responder(menssagem):
    res ="""
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /rolar para jogar dados
    """
    print("Mensagem não tratada:" + menssagem.text)
    bot.reply_to(menssagem,res)

bot.polling()