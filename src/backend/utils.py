from sqlmodel import select
from src.modelos import Personagens, Items

from src.singletons import DataBase

session = DataBase().session

def getCampanhas() -> list:
    comando = select(Personagens.campanha).distinct()
    matches = session.exec(comando).all()
    return matches

def getItens(campanha: str) -> list:
    comando = select(Items).where(Items.tag == campanha)
    matches = session.exec(comando).all()
    return matches

def getPersonagens(campanha: str) -> list:
    comando = select(Personagens).where(Personagens.campanha == campanha)
    matches = session.exec(comando).all()
    res = []
    for match in matches:
        res.append(match.dict())
    
    for r in res:
        try:
            r["status"] = eval(r["status"])
        except:
            pass
        i = eval(r["itens"])
        r["itens"] = getItensInfo(i)
    return res

def getInventario(id: int) -> list:
    comando = select(Personagens.itens).where(Personagens.id == id)
    match = session.exec(comando).first()
    if match:
        itens = eval(match)
        return getItensInfo(itens)
    return []

def getItensInfo(lista: list):
    if len(lista) == 1:
        lista.append(0)
    comando = f"""
    SELECT *
    FROM items
    WHERE id IN {tuple(lista)}
    """
    matches = session.exec(comando).all()
    return matches

def getStatus(id: int) -> dict:
    comando = select(Personagens.status).where(Personagens.id == id)
    match = session.exec(comando).first()
    if match:
        return eval(match)
    return {}

def createPersonagem(nome, campanha, status = {}):
    p = Personagens(nome=nome, itens="[]", status=status, campanha=campanha)
    session.add(p)
    session.commit()
    return {"sucesso": True}

def updateStatus(id, status):
    comando = select(Personagens).where(Personagens.id == id)
    match = session.exec(comando).first()
    if match:
        match.status = status
        session.commit()
        return {"sucesso": True}
    return {"sucesso": False}

def addItem(idPersonagem, idItem):
    comando = select(Personagens).where(Personagens.id == idPersonagem)
    match = session.exec(comando).first()
    if match:
        inv = eval(match.itens)
        inv.append(idItem)
        match.itens = str(inv)
        session.commit()
        return {"sucesso": True}
    return {"sucesso": False}

def removeItem(idPersonagem, idItem):
    comando = select(Personagens).where(Personagens.id == idPersonagem)
    match = session.exec(comando).first()
    try:
        if match:
            inv = eval(match.itens)
            inv.remove(idItem)
            match.itens = str(inv)
            session.commit()
            return {"sucesso": True}
    except:
        pass
    return {"sucesso": False}