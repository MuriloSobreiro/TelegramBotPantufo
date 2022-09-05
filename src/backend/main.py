from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import src.backend.utils as utils

app = FastAPI(title="RPG API", version="0.6.9")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API do Pantufo Bot no telegram"}

@app.get("/campanhas")
async def itens():
    return utils.getCampanhas()

@app.get("/itens")
async def itens(campanha: str):
    return utils.getItens(campanha)

@app.get("/personagens")
async def personagens(campanha: str):
    return utils.getPersonagens(campanha)

@app.get("/inventario")
async def inventario(id: int):
    return utils.getInventario(id)

@app.get("/status")
async def status(id: int):
    return utils.getStatus(id)

@app.post("/update_status")
async def updateStatus(id: int, status: str):
    return utils.updateStatus(id, status)

@app.post("/create_personagem")
async def createPersonagem(nome: str, campanha: str, status = {}):
    return utils.createPersonagem(nome, campanha, status)

@app.post("/addItem")
async def addItem(idPersonagem: int, idItem: int):
    return utils.addItem(idPersonagem,idItem)

@app.delete("/removeItem")
async def removeItem(idPersonagem: int, idItem: int):
    return utils.removeItem(idPersonagem, idItem)