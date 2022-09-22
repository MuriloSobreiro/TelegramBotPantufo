from sqlmodel import select

from modelos import Items
from singletons import DataBase, TelegramBot
import imgurApi
import teclados

item = {"nome": "", "descricao": "", "imagem": "", "atributos": "", "tag": ""}
session = DataBase.session
bot = TelegramBot().bot


def registrarNome(menssagem):
    item["nome"] = menssagem.text
    msg = bot.send_message(menssagem.chat.id, "Me envie a imagem ou o link da imagem.")
    bot.register_next_step_handler(msg, registrarImagem)


def registrarImagem(menssagem):
    if menssagem.content_type == "text":
        item["imagem"] = menssagem.text
        bot.send_message(menssagem.chat.id, "link registrado")
    else:
        m = bot.send_message(menssagem.chat.id, "Subindo imagem para Imgur")
        foto = bot.get_file_url(menssagem.photo[-1].file_id)
        url = uploadImgur(foto, item["nome"])
        if url:
            item["imagem"] = url
            bot.edit_message_text("Registro com sucesso ✅", m.chat.id, m.message_id)
        else:
            item["imagem"] = ""
            bot.edit_message_text("Falha ao salvar imagem ❌", m.chat.id, m.message_id)
    msg = bot.send_message(menssagem.chat.id, "Qual a Descrição?")
    bot.register_next_step_handler(msg, registrarDescricao)


def registrarDescricao(menssagem):
    item["descricao"] = menssagem.text
    comando = select(Items.tag).distinct()
    matches = session.exec(comando).all()
    keyboard = teclados.itemTags(matches)
    msg = bot.send_message(
        menssagem.chat.id, "Qual a tag do item?", reply_markup=keyboard
    )
    bot.register_next_step_handler(msg, registrarTag)


def registrarTag(menssagem):
    item["tag"] = menssagem.text
    salvaritem()
    bot.send_message(menssagem.chat.id, "Item salvo com sucesso")


def salvaritem():
    r = Items(**item)
    session.add(r)
    session.commit()


def uploadImgur(imagem, titulo, desc="") -> str:
    r = imgurApi.subirImagem(imagem, titulo, desc)
    if r:
        return r
    return ""


def visualizar(mensagem):
    print("listar item")
    bot.send_message(mensagem.chat.id, "Itens listados")


def editar(mensagem):
    print("editar item")
    bot.send_message(mensagem.chat.id, "Item Salvo com sucesso")


def deletar(mensagem):
    print("deletar item")
    bot.send_message(mensagem.chat.id, "Item deletado com sucesso")
