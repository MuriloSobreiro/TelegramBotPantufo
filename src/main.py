import re
from datetime import datetime, timedelta

import telebot
from sqlmodel import SQLModel
from telebot.types import Message
from loguru import logger

import rpg.itens as itens
import rpg.npcs as npcs
import rpg.rpg as rpg
import teclados
import termooo
from singletons import DataBase, TelegramBot

bot = TelegramBot().bot
session = DataBase().session
SQLModel.metadata.create_all(DataBase().engine)
logger.debug("Bot iniciado")

"""
Features:
Calculadora de Term.ooo
Rolagem de dados
/npc e /item

"""


@bot.message_handler(commands=["item", "i"], content_types=["text", "photo"])
def item(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: {mensagem.text}")
    comando = mensagem.text.split(" ")[-1].lower()
    if comando in ["registrar", "r"]:
        rpg.item = {}
        msg = bot.send_message(mensagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.registrarNome)
    elif comando in ["editar", "e"]:
        msg = bot.send_message(mensagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.editar)
    elif comando in ["deletar", "d"]:
        msg = bot.send_message(mensagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.deletar)
    elif comando in ["vizualizar", "v"]:
        msg = bot.send_message(mensagem.chat.id, "Qual o nome do item?")
        bot.register_next_step_handler(msg, itens.visualizar)
    else:
        bot.send_message(
            mensagem.chat.id,
            """
Você descobriu os comandos de itens, tente
/item registrar, para um novo item
/item visualizar, para ver os itens existentes
/item editar, para editar um item
/item deletar, para deletar um item
""",
        )


@bot.message_handler(commands=["npc", "n"], content_types=["text", "photo"])
def npc(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: {mensagem.text}")
    comandos = [m.lower() for m in mensagem.text.split(" ")]
    comando = comandos[-1]

    if comando in ["grupo", "g"]:
        g = npcs.getGrupos()
        msg = bot.send_message(
            mensagem.chat.id,
            "Escolha o grupo a editar",
            reply_markup=teclados.itemTags(g),
        )
        bot.register_next_step_handler(msg, npcs.setGrupo)

    elif comando in ["vizualizar", "v"]:
        g = npcs.getGrupos()
        msg = bot.send_message(
            mensagem.chat.id,
            "Escolha o grupo a visualizar",
            reply_markup=teclados.itemTags(g),
        )
        bot.register_next_step_handler(msg, npcs.visualizarGrupo)

    elif comando in ["registrar", "r"]:
        if not npcs.getGrupo(mensagem.from_user.id):
            bot.send_message(
                mensagem.chat.id,
                "Por favor escolha um grupo com /npc g",
                reply_markup=teclados.itemTags(["/npc grupo"]),
            )
            return
        msg = bot.send_message(mensagem.chat.id, "Qual o nome do NPC?")
        bot.register_next_step_handler(msg, npcs.registrar)

    elif comando in ["editar", "e"]:
        if not npcs.getGrupo(mensagem.from_user.id):
            bot.send_message(
                mensagem.chat.id,
                "Por favor escolha um grupo com /npc g",
                reply_markup=teclados.itemTags(["/npc grupo"]),
            )
            return
        msg = bot.send_message(
            mensagem.chat.id,
            "Qual o Nome do NPC?",
            reply_markup=teclados.itemTags(npcs.npcs(mensagem.from_user.id)),
        )
        bot.register_next_step_handler(msg, npcs.editar)

    elif comando in ["deletar", "d"]:
        if not npcs.getGrupo(mensagem.from_user.id):
            bot.send_message(
                mensagem.chat.id,
                "Por favor escolha um grupo com /npc g",
                reply_markup=teclados.itemTags(["/npc grupo"]),
            )
            return
        msg = bot.send_message(
            mensagem.chat.id,
            "Qual NPC dejesa deletar?",
            reply_markup=teclados.itemTags(npcs.npcs(mensagem.from_user.id)),
        )
        bot.register_next_step_handler(msg, npcs.deletar)

    else:
        bot.send_message(
            mensagem.chat.id,
            """
Você descobriu os comandos de npc, tente
/npc grupo, para escolher um grupo
/npc registrar, para um novo npc
/npc visualizar, para visualizar um npc
/npc editar, para editar um npc
/npc deletar, para deletar um npc
""",
            reply_markup=teclados.itemTags(
                [
                    "/npc grupo",
                    "/npc registrar",
                    "/npc vizualizar",
                    "/npc editar",
                    "/npc deletar",
                ]
            ),
        )


@bot.message_handler(commands=["util"])
def utils(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: /util")
    if mensagem.text.endswith("id"):
        bot.reply_to(mensagem, mensagem.from_user.id)


@bot.message_handler(commands=["termo", "termoo", "termooo"])
def termooResultado(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: {mensagem.text}")
    dia = re.findall(r"\d{4}-\d{1,2}-\d{1,2}", mensagem.text)
    chatId = mensagem.chat.id
    if mensagem.text.find("resultado") > 0:
        if dia:
            res = termooo.resultado(dia[0], chatId)
        elif mensagem.text.endswith("ontem"):
            res = termooo.resultado(str((datetime.now() - timedelta(1)).date()), chatId)
        else:
            res = termooo.resultado(chatId=chatId)
        bot.reply_to(mensagem, res)
    elif mensagem.text.find("config") > 0:
        if mensagem.text.find("addId") > 0:
            termooo.addId(chatId, mensagem.text.split()[-1])
            return
        ids = [mensagem.from_user.id]
        for e in mensagem.entities:
            if e.type == "text_mention":
                ids.append(e.user.id)
        termooo.saveJogadores(chatId, ids)

    else:
        bot.reply_to(
            mensagem,
            """
/termo resultado, para o resultado de hoje
/termo resultado ontem, para o resultado de ontem
/termo resultado YYYY-MM-DD, para um resultado anterior""",
        )


@bot.message_handler(commands=["rolar", "rola", "roll", "r"])
def rolarDados(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: {mensagem.text}")
    dados = re.findall(r"\d+d\d+", mensagem.text)
    if dados:
        res = rpg.rolarDados(dados[0])
        bot.reply_to(mensagem, res)
    elif mensagem.text.endswith("moeda") or mensagem.text.endswith("🪙"):
        res = rpg.rolarMoeda()
        bot.send_sticker(mensagem.from_user.id, res, reply_to_message_id=mensagem.id)
    elif mensagem.text.endswith("fechar"):
        bot.send_message(
            mensagem.chat.id,
            text="Fechando rolagem",
            reply_markup=telebot.types.ReplyKeyboardRemove(),
        )
    else:
        keyboard = teclados.rolagemDados()
        bot.send_message(
            mensagem.chat.id,
            reply_markup=keyboard,
            text="""
Esolha a rolagem com o teclado
OU Envie sua rolagem Ex:(1d5, 20d10, 69d420)
""",
        )


def termooVerify(mensagem: Message):
    if mensagem.content_type == "text":
        texto = mensagem.text
    else:
        texto = mensagem.caption
    if texto:
        return texto.startswith("joguei term.ooo") or texto.startswith("term.ooo")
    return False


@bot.message_handler(func=termooVerify, content_types=["text", "photo"])
def termooRegistro(menssagem: Message):
    logger.debug(f"{termooo.getNome(menssagem)}: Registro Termo")
    nome = termooo.getNome(menssagem)
    texto = termooo.getTexto(menssagem)
    res = termooo.registrar(texto, nome, menssagem.from_user.id)
    bot.reply_to(menssagem, "Registro: " + str(res))


def verificar(menssagem):
    return True


@bot.message_handler(
    func=verificar,
    content_types=[
        "audio",
        "photo",
        "voice",
        "video",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ],
)
def responder(mensagem: Message):
    logger.debug(f"{termooo.getNome(mensagem)}: {mensagem}")
    if mensagem.chat.type == "group":
        return
    res = """
    Não conheço esse comando, tente:
    - Enviar jogos de Term.ooo
    - /termo para resultados
    - /rolar para jogar dados
    """
    bot.reply_to(mensagem, res)


bot.polling()
