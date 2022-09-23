# **Pantufo o bot** 🤖

Um bot de Telegram feito em python com várias funcionalidades

### **Jogos** :

#### **Term.ooo**

* Registro de pontuações dos jogos
  * Solo
  * Dueto
  * Quarteto
* Avaliação de ganhadores
  * /termo resultado
* Configuração de participantes
  * /termo config
* Consulta do histórico
  * /termo resultado ontem
  * /termo resultado YYYY-MM-DD

### RPG

#### Rolagem de dados

* /rolar
  * rola os dados que forem requisitados e mostra o resultado
  * Ex: /rolar 1d20, /rolar 5d6, /rolar 17d22

#### NPCs

✅ /npc grupo
✅ /npc visualizar
✅ /npc registrar
✅ /npc editar
✅ /npc deletar

#### Itens

✅ /item registrar
🕙 /item editar
🕙 /item visualizar
🕙 /item deletar

### Backend

Uma API feita utilizando FastAPI para que um site externo tenha acesso aos itens registrados no banco

### **Bancos**

Esse bot utiliza dois bancos de dados para exercer as suas funções:

* SQLite - Local
  * Registro de jogos do termo
  * Registro de informações sobre itens do RPG
* DynamoDB - AWS
  * Registro das informções de NPCs do rpg
