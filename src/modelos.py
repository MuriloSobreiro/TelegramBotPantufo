from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class Termooo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idJogador: int
    jogador: str
    jogo: str
    numero: str
    pontos: str

class TermoooGroups(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chatId: int
    jogadores: str

class Items(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    atributos: str = Field(default="")
    imagem: str
    tag: str
    inclusao: datetime = Field(default=datetime.now())

class Personagens(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    itens: str
    status: str
    campanha: str
