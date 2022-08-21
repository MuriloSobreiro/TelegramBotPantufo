from typing import Optional

from sqlmodel import SQLModel, Field

class Termooo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idJogador: int
    jogador: str
    jogo: str
    numero: str
    pontos: str
