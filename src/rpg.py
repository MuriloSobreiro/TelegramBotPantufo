from random import randint
import numpy as np
from singletons import TelegramBot

item = {"nome":"","descricao":"","imagem":"","atributos":"","tag":""}

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
    print(item)
    msg = bot.send_message(menssagem.chat.id, "Me envie o link da imagem.")
    bot.register_next_step_handler(msg, registrarImagem)

def registrarImagem(menssagem):
    print(menssagem)
    if menssagem.content_type == "text":
        bot.send_message(menssagem.chat.id, "link registrado")
        item["imagem"] = menssagem.text
    else:
        bot.send_message(menssagem.chat.id, "registro de imagens não implementado")
    print(item)
    msg = bot.send_message(menssagem.chat.id, "Qual a Descrição?")
    bot.register_next_step_handler(msg, registrarDescricao)

def registrarDescricao(menssagem):
    item["descricao"] = menssagem.text
    print(item)
    msg = bot.send_message(menssagem.chat.id, "Qual a tag do item?")
    bot.register_next_step_handler(msg, registrarTag)

def registrarTag(menssagem):
    item["tag"] = menssagem.text
    print(item)

def guardarImagem(imagem) -> str:
    return "Não guardado"
