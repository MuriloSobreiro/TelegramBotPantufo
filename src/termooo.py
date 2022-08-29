from datetime import datetime
import re
import pandas as pd
import itertools
from sqlmodel import Session, SQLModel, create_engine, select
from modelos import *

engine = create_engine("sqlite:///database.db", connect_args={'check_same_thread': False})
session = Session(engine)

SQLModel.metadata.create_all(engine)

trad = {"term.ooo/2": 8,"term.ooo/4": 10}
frases = ["Por pouquíssimo","Por pouco", "Sem dificuldades","Esmagadora"]

def registrar(texto, jogador, idjogador):
    info = processaTermo(texto)
    info["jogador"] = jogador
    info["idJogador"] = idjogador
    res = salvarNoBanco(info)
    print(info)
    return res

def resultado(dia: str = str(datetime.now().date()), jogadores: list = None):
    dados = getNoBanco(dia)
    jogos = getJogo(dia)
    infos = processaDados(dados)
    resultados = processaInfos(infos)
    res = criaMensagem(infos, resultados, dia, jogos)
    return res


def processaTermo(texto: str):
    res = re.findall(r"term\.ooo.+", texto)[0]
    res = res.split(' ')
    jogo = res[0]
    id = res[1][1:]
    if res[0] == "term.ooo":
        ponto = res[2].replace('*',"")[0]
        pontos = [int(ponto) if ponto !="X" else 7]
    else:
        a = texto.split("\n")
        pontos = a[2]+a[3]
        pontos = [ord(x) -48 for x in pontos]#Converte emoji em numero
        pontos = [p for p in pontos if (p < 10 or p == 128949)]#Remove emojis a mais
        pontos = [trad[res[0]] if p == 128949 else p for p in pontos]#Troca falhas por pontuacao
    info  = {"jogo": jogo, "numero": id, "pontos": str(pontos)}
    return info

def processaDados(dados) -> dict:
    df = pd.DataFrame.from_records(dados,columns=["id","jogador","pontos"])
    df["pontos"] = df["pontos"].apply(lambda x: eval(x))
    df["tam"] = df["pontos"].apply(lambda x: len(x))
    df.sort_values(["id","tam"],inplace=True)
    results = df.groupby("id")["pontos"].apply(list).to_dict()
    for id in set(df["id"].to_list()):
        results[df.loc[df["id"] == id]["jogador"].to_list()[0]] = results.pop(id)
    return results

def processaInfos(results) -> dict:
    jogos = ["", "indefinido", "indefinido", "","indefinido"]
    ganhador = "Indefinido"
    frase = "Indefinido"
    medias = []
    menor = [0, 11, 11, 0, 11]
    jogadores = []
    for k in results:
        nome = k.split()[0]
        jogadores.append(nome)
        medias.append((nome, sum(itertools.chain.from_iterable(results[k]))/7))
        for pontos in results[k]:
            l = len(pontos)
            p = max(pontos)
            if p < menor[l]:
                jogos[l] = nome
                menor[l] = p
            elif p == menor[l]:
                jogos[l] = "Empate"
    c = 0
    for j in jogadores:
        p = jogos.count(j)
        if p > c:
            c = p
            ganhador = j
        elif p == c:
            ganhador = "Indefinido"
        frase = frases[p]
    
    t = 10
    if ganhador == "Indefinido":
        for m in medias:
            if m[1] < t:
                t = m[1]
                ganhador = m[0]
            elif m[1] == t:
                ganhador == "Indefinido"
        frase = frases[0]

    return {"jogos":jogos, "ganhador": ganhador, "frase": frase, "medias":medias}

def criaMensagem(infos, resultados, dia, jogos) -> str:
    res = dia
    for k in infos:
        pontos = ["","Não Registrado","Não Registrado","","Não Registrado"]
        for p in infos[k]:
            p = [str(t) for t in p]
            pontos[len(p)] = ", ".join(p)
        temp = f"""
{k}
Original - {pontos[1]}
Dueto    - {pontos[2]}
Quarteto - {pontos[4]} 
"""
        res = res + temp

    result = f"""
Resultados
Original - {resultados["jogos"][1]} #{jogos[0]}
Dueto    - {resultados["jogos"][2]} #{jogos[1]}
Quarteto - {resultados["jogos"][4]} #{jogos[1]}

Ganhador: {resultados["ganhador"]}
Vitória: {resultados["frase"]}
Médias:
"""
    for m in resultados["medias"]:
        result = result + f"{m[0]}: {m[1]}\n"
    return res + result

def salvarNoBanco(info: dict):
    r = Termooo(**info)
    comando = select(Termooo).where(Termooo.idJogador == r.idJogador).where(Termooo.numero == r.numero).where(Termooo.jogo == r.jogo)
    matches = session.exec(comando).all()
    if(len(matches)==0):
        session.add(r)
        session.commit()
        return "Com Sucesso"
    else:
        return "Já Existe"

def getNoBanco(dia: str):
    jogos = getJogo(dia)
    comando = f"""
    SELECT idJogador, jogador, pontos
    FROM termooo
    WHERE (jogo = 'term.ooo' AND numero = '{jogos[0]}')
    OR (NOT jogo = 'term.ooo' AND numero = '{jogos[1]}')
    """
    matches = session.exec(comando).all()
    return matches

def getJogo(dia: str):
    date_format = "%Y-%m-%d"
    objetivo = datetime.strptime(dia,date_format)
    hoje = datetime.now()
    delta = (hoje-objetivo).days
    jogos = jogoAtual()
    return [jogos[0]-delta,jogos[1]-delta]

def jogoAtual():
    date_format = "%Y-%m-%d"
    objetivo = datetime.strptime("2022-08-26",date_format)
    hoje = datetime.now()
    delta = (hoje-objetivo).days
    return [236+delta,185+delta]
