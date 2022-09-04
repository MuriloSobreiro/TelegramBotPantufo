from datetime import datetime, timedelta
import re
import telebot
from singletons import DataBase, TelegramBot
import teclados
from sqlmodel import SQLModel

import termooo
import rpg

bot = TelegramBot().bot
session = DataBase().session
SQLModel.metadata.create_all(DataBase().engine)
print("Bot iniciado")

"""
Features:
Calculadora de Term.ooo
Rolagem de dados


"""
@bot.message_handler(commands=["registrar"], content_types=["text","photo"])
def registrar(menssagem):
    if menssagem.text.endswith("item"):
        rpg.item = {}
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, rpg.registrarNome)

@bot.message_handler(commands=["util"])
def utils(menssagem):
    if menssagem.text.endswith("id"):
        bot.reply_to(menssagem,menssagem.from_user.id)

@bot.message_handler(commands=["termo","termoo","termooo"])
def termooResultado(menssagem):
    dia = re.findall(r"\d{4}-\d{1,2}-\d{1,2}", menssagem.text)
    chatId = menssagem.chat.id
    if menssagem.text.find("resultado") > 0:
        if dia:
            res = termooo.resultado(dia[0],chatId)
        elif menssagem.text.endswith("ontem"):
            res = termooo.resultado(str((datetime.now()-timedelta(1)).date()),chatId)
        else:
            res = termooo.resultado(chatId=chatId)
        bot.reply_to(menssagem,res)
    elif menssagem.text.find("config") > 0:
        if menssagem.text.find("addId") > 0:
            termooo.addId(chatId, menssagem.text.split()[-1])
            return
        ids = [menssagem.from_user.id]
        for e in menssagem.entities:
            if e.type == "text_mention":
                ids.append(e.user.id)
        termooo.saveJogadores(chatId,ids)

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
    if texto:
        return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")
    return False

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
    print("Mensagem não tratada:")
    print(menssagem)
    if menssagem.chat.type == "group":
        return
    res ="""
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /termo para resultados
    - /rolar para jogar dados
    """
    bot.reply_to(menssagem,res)

bot.polling()