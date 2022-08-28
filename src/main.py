import os
import re
import telebot
import teclados
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
    elif menssagem.text.endswith("moeda") or menssagem.text.endswith("🪙"):
        print(menssagem)
        res = rpg.rolarMoeda()
        bot.send_sticker(menssagem.from_user.id,res,reply_to_message_id=menssagem.id)
    elif menssagem.text.endswith("fechar"):
        bot.send_message(menssagem.chat.id, text='Fechando rolagem', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        keyboard = teclados.rolagemDados()
        bot.send_message(menssagem.chat.id, text='Escolha a rolagem', reply_markup=keyboard)
    print("Rolagem de dados: " + menssagem.text)

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

@bot.message_handler(func=verificar,content_types=['audio', 'photo', 'voice', 'video', 'document','text', 'location', 'contact', 'sticker'])
def responder(menssagem):
    res ="""
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /rolar para jogar dados
    """
    print("Mensagem não tratada:")
    print(menssagem)
    bot.reply_to(menssagem,res)

bot.polling()