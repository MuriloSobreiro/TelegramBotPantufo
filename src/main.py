from datetime import datetime, timedelta
import re
import telebot
from telebot.types import Message
from singletons import DataBase, TelegramBot
import teclados
from sqlmodel import SQLModel

import termooo
import rpg.rpg as rpg
import rpg.itens as itens
import rpg.npcs as npcs

bot = TelegramBot().bot
session = DataBase().session
SQLModel.metadata.create_all(DataBase().engine)
print("Bot iniciado")

"""
Features:
Calculadora de Term.ooo
Rolagem de dados
/npc e /item

"""
@bot.message_handler(commands=["item","i"], content_types=["text","photo"])
def item(menssagem: Message):
    comando = menssagem.text.split(" ")[-1].lower()
    if comando in ["registrar", "r"]:
        rpg.item = {}
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.registrarNome)
    elif comando in ["editar", "e"]:
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.editar)
    elif comando in ["deletar", "d"]:
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.deletar)
    elif comando in ["vizualizar", "v"]:
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.visualizar)
    else:
        bot.send_message(menssagem.chat.id, """
Você descobriu os comandos de itens, tente
/item registrar, para um novo item
/item visualizar, para ver os itens existentes
/item editar, para editar um item
/item deletar, para deletar um item
""")

@bot.message_handler(commands=["npc","n"], content_types=["text","photo"])
def item(menssagem: Message):
    comandos = [m.lower() for m in menssagem.text.split(" ")]
    comando = comandos[-1]
    
    if comando in ["grupo", "g"]:
        g = npcs.getGrupos()
        msg = bot.send_message(menssagem.chat.id, "Escolha o grupo a editar", reply_markup=teclados.itemTags(g))
        bot.register_next_step_handler(msg, npcs.setGrupo)

    elif comando in ["vizualizar", "v"]:
        g = npcs.getGrupos()
        msg = bot.send_message(menssagem.chat.id, "Escolha o grupo a visualizar", reply_markup=teclados.itemTags(g))
        bot.register_next_step_handler(msg, npcs.visualizarGrupo)
    
    elif comando in ["registrar", "r"]:
        if not npcs.getGrupo():
            bot.send_message(menssagem.chat.id,"Por favor escolha um grupo com /npc g", reply_markup=teclados.itemTags(["/npc grupo"]))
            return
        msg = bot.send_message(menssagem.chat.id, "Qual o nome do NPC?")
        bot.register_next_step_handler(msg, npcs.registrar)

    elif comando in ["editar", "e"]:
        if not npcs.getGrupo():
            bot.send_message(menssagem.chat.id,"Por favor escolha um grupo com /npc g", reply_markup=teclados.itemTags(["/npc grupo"]))
            return
        msg = bot.send_message(menssagem.chat.id, "Qual o Nome do NPC?", reply_markup=teclados.itemTags(npcs.npcs()))
        bot.register_next_step_handler(msg, npcs.editar)
    
    elif comando in ["deletar", "d"]:
        if not npcs.getGrupo():
            bot.send_message(menssagem.chat.id,"Por favor escolha um grupo com /npc g", reply_markup=teclados.itemTags(["/npc grupo"]))
            return
        msg = bot.send_message(menssagem.chat.id, "Qual NPC dejesa deletar?", reply_markup=teclados.itemTags(npcs.npcs()))
        bot.register_next_step_handler(msg, npcs.deletar)
    
    else:
        bot.send_message(menssagem.chat.id, """
Você descobriu os comandos de npc, tente
/npc grupo, para escolher um grupo
/npc registrar, para um novo npc
/npc visualizar, para visualizar um npc
/npc editar, para editar um npc
/npc deletar, para deletar um npc
""", reply_markup=teclados.itemTags(["/npc grupo", "/npc registrar", "/npc vizualizar", "/npc editar", "/npc deletar"]))

@bot.message_handler(commands=["util"])
def utils(menssagem: Message):
    if menssagem.text.endswith("id"):
        bot.reply_to(menssagem,menssagem.from_user.id)

@bot.message_handler(commands=["termo","termoo","termooo"])
def termooResultado(menssagem: Message):
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
def rolarDados(menssagem: Message):
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

def termooVerify(menssagem: Message):
    if menssagem.content_type == "text":
        texto = menssagem.text
    else:
        texto = menssagem.caption
    if texto:
        return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")
    return False

@bot.message_handler(func=termooVerify, content_types=["text","photo"])
def termooRegistro(menssagem: Message):
    nome = termooo.getNome(menssagem)
    texto = termooo.getTexto(menssagem)
    res = termooo.registrar(texto, nome, menssagem.from_user.id)
    bot.reply_to(menssagem,"Registro: " + str(res))
    print("Registro de Termooo")

def verificar(menssagem):
    return True

@bot.message_handler(func=verificar,content_types=['audio', 'photo', 'voice', 'video', 'document','text', 'location', 'contact', 'sticker'])
def responder(menssagem: Message):
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