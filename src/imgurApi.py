import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()


def subirImagem(imagem, titulo: str, desc: str = ""):
    header = {"Authorization": f"Client-ID {os.environ['IMGURID']}"}
    body = {"image": imagem, "type": "url", "title": titulo, "description": desc}

    response = requests.post(
        "https://api.imgur.com/3/upload", headers=header, data=body
    ).json()
    if response["success"]:
        return response["data"]["link"]
    return False
