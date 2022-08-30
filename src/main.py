from datetime import datetime, timedelta
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
@bot.message_handler(commands=["termo","termoo","termooo"])
def termooResultado(menssagem):
    dia = re.findall(r"\d{4}-\d{1,2}-\d{1,2}", menssagem.text)
    if menssagem.text.find("resultado") > 0:
        if dia:
            res = termooo.resultado(dia[0])
        elif menssagem.text.endswith("ontem"):
            res = termooo.resultado(str((datetime.now()-timedelta(1)).date()))
        else:
            res = termooo.resultado()
        bot.reply_to(menssagem,res)
    else:
        bot.reply_to(menssagem,"""
/termo resultado, para o resultado de hoje
/termo resultado ontem, para o resultado de ontem
/termo resultado YYYY-MM-DD, para um resultado anterior""")

    print("Resultado termooo")
@bot.message_handler(commands=["rolar","rola","roll","r"])
def rolarDados(menssagem):
    dados = re.findall(r"\d+d\d+", menssagem.text)
    if dados:
        res = rpg.rolarDados(dados[0])
        bot.reply_to(menssagem,res)
    elif menssagem.text.endswith("moeda") or menssagem.text.endswith("🪙"):
        res = rpg.rolarMoeda()
        bot.send_sticker(menssagem.from_user.id,res,reply_to_message_id=menssagem.id)
    elif menssagem.text.endswith("fechar"):
        bot.send_message(menssagem.chat.id, text='Fechando rolagem', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        keyboard = teclados.rolagemDados()
        bot.send_message(menssagem.chat.id, reply_markup=keyboard, text="""
Esolha a rolagem com o teclado
OU Envie sua rolagem Ex:(1d5, 20d10, 69d420)
""")
    print("Rolagem de dados: " + menssagem.text)

def termooVerify(menssagem):
    if menssagem.content_type == "text":
        texto = menssagem.text
    else:
        texto = menssagem.caption
    return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")

@bot.message_handler(func=termooVerify, content_types=["text","photo"])
def termooRegistro(menssagem):
    nome = termooo.getNome(menssagem)
    texto = termooo.getTexto(menssagem)
    res = termooo.registrar(texto, nome, menssagem.from_user.id)
    bot.reply_to(menssagem,"Registro: " + str(res))
    print("Registro de Termooo")

def verificar(menssagem):
    return True

@bot.message_handler(func=verificar,content_types=['audio', 'photo', 'voice', 'video', 'document','text', 'location', 'contact', 'sticker'])
def responder(menssagem):
    if menssagem.chat.type == "group":
        return
    res ="""
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /termo para resultados
    - /rolar para jogar dados
    """
    print("Mensagem não tratada:")
    print(menssagem)
    bot.reply_to(menssagem,res)

bot.polling()