import singletons

bot = singletons.TelegramBot().bot


def registrar(mensagem):
    print("registrar npc")
    bot.send_message(mensagem.chat.id, "NPC registrado")

def visualizar(mensagem):
    print("listar npc")
    bot.send_message(mensagem.chat.id, "NPCs listados")

def editar(mensagem):
    print("editar npc")
    bot.send_message(mensagem.chat.id, "NPC Salvo com sucesso")

def deletar(mensagem):
    print("deletar npc")
    bot.send_message(mensagem.chat.id, "NPC deletado com sucesso")
