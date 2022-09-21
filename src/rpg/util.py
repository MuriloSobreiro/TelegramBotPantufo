import boto3
from dotenv import load_dotenv

load_dotenv()
dynamo = boto3.client('dynamodb',region_name='sa-east-1')
tabela = "NPCs"

def pk(nome:str, grupo:str):
    return {
            "Nome": {
                'S': nome
            },
            "Grupo": {
                'S': grupo
            }
        }

def getGrupos() -> list:
    res = dynamo.scan(
        TableName=tabela,
        IndexName="Grupo-index",
        Select="SPECIFIC_ATTRIBUTES",
        AttributesToGet=["Grupo"]
    )
    return list(set([r["Grupo"]["S"] for r in res["Items"]]))

def getNPCs(grupo: str) -> list:
    res = dynamo.query(
        TableName= tabela,
        IndexName= "Grupo-index",
        KeyConditionExpression= "Grupo = :grupo",
        ExpressionAttributeValues= {
            ":grupo":{"S": grupo}
        }
    )
    return [r["Nome"]["S"] for r in res["Items"]]

def getNPCInfo(nome:str, grupo:str):
    res = dynamo.get_item(
        TableName=tabela,
        Key = pk(nome, grupo)
    )
    r = {}
    for k in res["Item"]:
        r[k] = res["Item"][k]['S']
    return r

def addNPC(nome:str, grupo:str) -> bool:
    params = pk(nome, grupo)
    try:
        dynamo.put_item(TableName=tabela,Item=params)
        return True
    except Exception as e:
        print(e)
        return False

def deleteNPC(nome:str, grupo:str) -> bool:
    params = pk(nome, grupo)
    try:
        dynamo.delete_item(TableName=tabela,Key=params)
        return True
    except Exception as e:
        print(e)
        return False

def editItemNPC(params: dict, atributo:str, valor:str) -> bool:
    for k in params:
        params[k] = {'S': params[k]}
    params[atributo] = {'S': valor}
    try:
        dynamo.put_item(TableName=tabela,Item=params)
        return True
    except Exception as e:
        print(e)
        return False

def deleteItemNPC(nome:str, grupo:str, atributo:str) -> bool:
    params = pk(nome, grupo)
    dynamo.update_item(
        TableName=tabela,
        Key=params,
        UpdateExpression=f"REMOVE {atributo}"
    )
    return True

if __name__ == "__main__":
    t = getGrupos()
    print(t)
    p = getNPCs(t[0])
    print(p)
    print(getNPCInfo(p[0],t[0]))
    