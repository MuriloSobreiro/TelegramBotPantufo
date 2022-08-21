import re

from sqlmodel import Session, SQLModel, create_engine, select
from modelos import *

engine = create_engine("sqlite:///database.db", connect_args={'check_same_thread': False})
session = Session(engine)

SQLModel.metadata.create_all(engine)

trad = {"term.ooo/2": 8,"term.ooo/4": 10}

def registrar(texto, jogador):
    info = processaTermo(texto)
    info["jogador"] = jogador
    res = salvarNoBanco(info)
    return res

def resultado(dia):
    return "Não dados"


def processaTermo(texto):
    res = re.findall(r"term\.ooo.+", texto)[0]
    res = res.split(' ')
    jogo = res[0]
    id = res[1][1:]
    if res[0] == "term.ooo":
        pontos = [res[2][0]]
    else:
        a = texto.split("\n")
        pontos = a[2]+a[3]
        pontos = [ord(x) -48 for x in pontos]
        pontos = [p for p in pontos if (p < 10 or p == 128949)]
        pontos = [trad[res[0]] if p == 128949 else p for p in pontos]
    info  = {"jogo": jogo, "numero": id, "pontos": str(pontos)}
    return info

def salvarNoBanco(info: dict):
    r = Termooo(**info)
    comando = select(Termooo).where(Termooo.jogador == r.jogador).where(Termooo.numero == r.numero).where(Termooo.jogo == r.jogo)
    matches = session.exec(comando).all()
    if(len(matches)==0):
        session.add(r)
        session.commit()
        return "Com Sucesso"
    else:
        return "Já Existe"
