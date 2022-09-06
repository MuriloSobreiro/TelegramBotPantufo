from random import randint
import numpy as np
from modelos import Items
from sqlmodel import select
from singletons import DataBase, TelegramBot
import imgurApi
import teclados

item = {"nome":"","descricao":"","imagem":"","atributos":"","tag":""}
session = DataBase.session

def rolarDados(dados: str) -> str:
    res = f"{dados}🎲: "
    soma = 0
    if dados:
        try:
            d = dados.split('d')
            d = (int(d[0]),int(d[1]))
            limit = 20
            limit = d[0] if d[0] < limit else 20
            numeros = np.random.randint(1,d[1],d[0])
            soma = numeros.sum()
            res = res + ', '.join([str(int) for int in numeros[0:limit]])
            if d[0] > limit:
                res = res + f",..., {str(numeros[-1])}"
        except:
            return "Impossível fazer essa rolagem"
            
          
    return f"{res} = {soma}"

def rolarMoeda():
    r = ["CAACAgEAAxkBAAIBx2MK2QAB52-S-AT6NFB5ii-C9KPlWwACEQIAAhKiUETlVaD1jaRdnikE","CAACAgEAAxkBAAIB0mMK20vynNzqCQ6V3uPNP7hRtYW4AAIKAANK8GFNl91huJOv1TEpBA"]
    return r[randint(0,1)]

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
            bot.edit_message_text("Registro com sucesso ✅", m.chat.id,m.message_id)
        else:
            item["imagem"] = ""
            bot.edit_message_text("Falha ao salvar imagem ❌", m.chat.id,m.message_id)
    msg = bot.send_message(menssagem.chat.id, "Qual a Descrição?")
    bot.register_next_step_handler(msg, registrarDescricao)

def registrarDescricao(menssagem):
    item["descricao"] = menssagem.text
    comando = select(Items.tag).distinct()
    matches = session.exec(comando).all()
    keyboard = teclados.itemTags(matches)
    msg = bot.send_message(menssagem.chat.id, "Qual a tag do item?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, registrarTag)

def registrarTag(menssagem):
    item["tag"] = menssagem.text
    salvaritem()
    bot.send_message(menssagem.chat.id, "Item salvo com sucesso")
    
def salvaritem():
    r = Items(**item)
    session.add(r)
    session.commit()

def uploadImgur(imagem,titulo,desc = "") -> str:
    r = imgurApi.subirImagem(imagem,titulo,desc)
    if r:
        return r
    return ""
