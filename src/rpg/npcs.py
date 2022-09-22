import singletons
from telebot.types import Message, ReplyKeyboardRemove
from rpg.util import deleteNPC, getGrupos, addNPC, getNPCInfo, getNPCs, editItemNPC
import os
import teclados

bot = singletons.TelegramBot().bot


def grupos():
    return getGrupos()


def setGrupo(mensagem: Message):
    os.environ["Grupo"] = mensagem.text
    g = os.environ["Grupo"]
    bot.send_message(
        mensagem.chat.id,
        f"✅ {g} selecionado",
        reply_markup=teclados.itemTags(
            ["/npc registrar", "/npc vizualizar", "/npc editar", "/npc deletar"]
        ),
    )


def getGrupo():
    try:
        g = os.environ["Grupo"]
        return g
    except:
        return ""


def registrar(mensagem: Message):
    try:
        if addNPC(mensagem.text, os.environ["Grupo"]):
            bot.send_message(mensagem.chat.id, "✅ NPC registrado")
    except:
        bot.send_message(mensagem.chat.id, "❌ Falha ao registrar")


def npcs():
    return getNPCs(os.environ["Grupo"])


def visualizarGrupo(mensagem: Message):
    os.environ["Grupo"] = mensagem.text
    g = os.environ["Grupo"]
    bot.send_message(mensagem.chat.id, f"✅ {g} selecionado")
    msg = bot.send_message(
        mensagem.chat.id, "Qual o nome do NPC?", reply_markup=teclados.itemTags(npcs())
    )
    bot.register_next_step_handler(msg, visualizar)


def visualizar(mensagem: Message):
    r = getNPCInfo(mensagem.text, os.environ["Grupo"])
    m = formatNPCInfo(r)
    bot.send_message(mensagem.chat.id, m, parse_mode="HTML")


def editar(mensagem: Message):
    r = getNPCInfo(mensagem.text, os.environ["Grupo"])
    m = formatNPCInfo(r)
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
    if texto.lower() == "sair":
        if not teclado[0] == 0:
            bot.delete_message(teclado[0], teclado[1])
        bot.edit_message_text(f"✅ Edição finalizada", prompt[0], prompt[1])
        bot.delete_message(mensagem.chat.id, mensagem.message_id)
        return
    elif atributo:
        bot.delete_message(mensagem.chat.id, mensagem.message_id)
        bot.delete_message(teclado[0], teclado[1])
        msg = bot.edit_message_text(f"Qual o valor de {texto}", prompt[0], prompt[1])
        bot.register_next_step_handler(
            msg, editarAtributo, ficha, prompt, nome, (0, 0), texto, False
        )
    else:
        r = getNPCInfo(nome, os.environ["Grupo"])
        editItemNPC(r, nomeAtributo, texto)
        r = getNPCInfo(nome, os.environ["Grupo"])
        m = formatNPCInfo(r)
        bot.edit_message_text(m, ficha[0], ficha[1], parse_mode="HTML")
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
    bot.register_next_step_handler(msg, deletarConfirma, mensagem.text)


def deletarConfirma(mensagem: Message, p):
    if mensagem.text.lower() in ["sim", "s", "yes", "y", "👌", "👍"]:
        if deleteNPC(p, os.environ["Grupo"]):
            bot.send_message(mensagem.chat.id, f"✅ {mensagem.text} deletado")
        else:
            bot.send_message(mensagem.chat.id, f"❌ {mensagem.text} falha ao deletar")
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
