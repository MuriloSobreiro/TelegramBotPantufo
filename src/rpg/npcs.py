import singletons
from telebot.types import Message, ReplyKeyboardRemove
from rpg.util import deleteNPC, getGrupos, addNPC, getNPCInfo, getNPCs, editItemNPC
from loguru import logger

import imgurApi
import teclados

bot = singletons.TelegramBot().bot
grupo = {}


def checkAbort(texto):
    return texto.lower() in ["sair", "cancelar", "abortar"]


def grupos():
    return getGrupos()


def setGrupo(mensagem: Message):
    grupo[mensagem.from_user.id] = mensagem.text
    g = grupo[mensagem.from_user.id]
    logger.debug(f"Grupo selecionado: {g}")
    bot.send_message(
        mensagem.chat.id,
        f"✅ {g} selecionado",
        reply_markup=teclados.itemTags(
            ["/npc registrar", "/npc vizualizar", "/npc editar", "/npc deletar"]
        ),
    )


def getGrupo(id):
    try:
        g = grupo[id]
        return g
    except:
        return ""


def registrar(mensagem: Message):
    if checkAbort(mensagem.text):
        bot.send_message(mensagem.chat.id, "❌ Operação abortada!")
        return
    try:
        if addNPC(mensagem.text, grupo[mensagem.from_user.id]):
            logger.debug(f"NPC Registrado: {mensagem.text}")
            bot.send_message(mensagem.chat.id, "✅ NPC registrado")
    except:
        logger.error(f"Falha ao registrar NPC")
        bot.send_message(mensagem.chat.id, "❌ Falha ao registrar")


def npcs(id):
    return getNPCs(grupo[id])


def visualizarGrupo(mensagem: Message):
    grupo[mensagem.from_user.id] = mensagem.text
    g = grupo[mensagem.from_user.id]
    bot.send_message(mensagem.chat.id, f"✅ {g} selecionado")
    msg = bot.send_message(
        mensagem.chat.id,
        "Qual o nome do NPC?",
        reply_markup=teclados.itemTags(npcs(mensagem.from_user.id)),
    )
    bot.register_next_step_handler(msg, visualizar)


def visualizar(mensagem: Message):
    r = getNPCInfo(mensagem.text, grupo[mensagem.from_user.id])
    m = formatNPCInfo(r)
    logger.debug(f"Vizualizando: {mensagem.text}")
    bot.send_message(mensagem.chat.id, m, parse_mode="HTML")


def editar(mensagem: Message):
    if checkAbort(mensagem.text):
        bot.send_message(mensagem.chat.id, "❌ Operação abortada!")
        return
    r = getNPCInfo(mensagem.text, grupo[mensagem.from_user.id])
    m = formatNPCInfo(r)
    logger.debug(f"Editando: {mensagem.text}")
    ficha = bot.send_message(mensagem.chat.id, m, parse_mode="HTML")
    msg = bot.send_message(
        mensagem.chat.id,
        "Digite o nome do atributo para editar\nOu sair para finalizar a edição",
    )
    teclado = bot.send_message(
        mensagem.chat.id,
        "Atributos já existentes:",
        reply_markup=teclados.itemTags(r.keys() - ["Nome", "Grupo"]),
    )
    bot.register_next_step_handler(
        msg,
        editarAtributo,
        (ficha.chat.id, ficha.message_id),
        (msg.chat.id, msg.message_id),
        mensagem.text,
        (teclado.chat.id, teclado.message_id),
    )


def editarAtributo(
    mensagem: Message,
    ficha: tuple,
    prompt: tuple,
    nome: str,
    teclado: tuple = (0, 0),
    nomeAtributo: str = "",
    atributo: bool = True,
):
    texto = mensagem.text
    if texto and checkAbort(mensagem.text):
        if not teclado[0] == 0:
            bot.delete_message(teclado[0], teclado[1])
        bot.edit_message_text(f"✅ Edição finalizada", prompt[0], prompt[1])
        bot.delete_message(mensagem.chat.id, mensagem.message_id)
        return
    elif atributo:
        logger.debug(f"Editando atributo: {texto}")
        bot.delete_message(mensagem.chat.id, mensagem.message_id)
        bot.delete_message(teclado[0], teclado[1])
        msg = bot.edit_message_text(f"Qual o valor de {texto}", prompt[0], prompt[1])
        bot.register_next_step_handler(
            msg, editarAtributo, ficha, prompt, nome, (0, 0), texto, False
        )
    else:
        if nomeAtributo in ["foto", "Foto"]:
            nomeAtributo = "Foto"
            if mensagem.content_type == "photo":
                m = bot.send_message(mensagem.chat.id, "Subindo imagem para Imgur")
                foto = bot.get_file_url(mensagem.photo[-1].file_id)
                url = uploadImgur(foto, nomeAtributo + nome)
                texto = url
                if url:
                    bot.edit_message_text(
                        "Registro com sucesso ✅", m.chat.id, m.message_id
                    )
                else:
                    bot.edit_message_text(
                        "Falha ao salvar imagem ❌", m.chat.id, m.message_id
                    )
        r = getNPCInfo(nome, grupo[mensagem.from_user.id])
        editItemNPC(r, nomeAtributo, texto)
        r = getNPCInfo(nome, grupo[mensagem.from_user.id])
        m1 = formatNPCInfo(r)
        bot.edit_message_text(m1, ficha[0], ficha[1], parse_mode="HTML")
        bot.delete_message(mensagem.chat.id, mensagem.message_id)
        msg = bot.edit_message_text(
            "Digite o nome do atributo para editar\nOu sair para finalizar a edição",
            prompt[0],
            prompt[1],
        )
        k = bot.send_message(
            mensagem.chat.id,
            "Atributos já existentes:",
            reply_markup=teclados.itemTags(r.keys() - ["Nome", "Grupo"]),
        )
        bot.register_next_step_handler(
            msg, editarAtributo, ficha, prompt, nome, (k.chat.id, k.message_id)
        )


def deletar(mensagem: Message):
    msg = bot.send_message(
        mensagem.chat.id,
        f"Você Tem certeza que quer deletar {mensagem.text}?\nESSA AÇÃO É IRREVERSSÍVEL",
    )
    logger.warning(f"Deletando NPC: {mensagem.text}")
    bot.register_next_step_handler(msg, deletarConfirma, mensagem.text)


def deletarConfirma(mensagem: Message, p):
    if mensagem.text.lower() in ["sim", "s", "yes", "y", "👌", "👍"]:
        if deleteNPC(p, grupo[mensagem.from_user.id]):
            logger.warning(f"NPC Deletado: {mensagem.text}")
            bot.send_message(mensagem.chat.id, f"✅ {p} deletado")
        else:
            bot.send_message(mensagem.chat.id, f"❌ {p} falha ao deletar")
    else:
        bot.send_message(mensagem.chat.id, "❌ Operação abortada!")


def formatNPCInfo(info: dict) -> str:
    res = f"""<b>{info["Nome"]}</b>
<b>==============</b>"""
    for k in info:
        if k == "Nome":
            continue
        res = res + f"\n{k}:\n    {info[k]}"
    res = res + "\n<b>==============</b>"
    return res


def uploadImgur(imagem, titulo, desc="") -> str:
    r = imgurApi.subirImagem(imagem, titulo, desc)
    if r:
        return r
    return ""
