import numpy as np

def rolarDados(dados: str) -> str:
    res = f"{dados}🎲: "
    soma = 0
    if dados:
        try:
            d = dados.split('d')
            d = (int(d[0]),int(d[1]))
            limit = 20
            limit = d[0] if d[0] < limit else 20
            numeros = np.random.randint(1,d[1],d[0])
            soma = numeros.sum()
            res = res + ', '.join([str(int) for int in numeros[0:limit]])
            if d[0] > limit:
                res = res + f",..., {str(numeros[-1])}"
        except:
            return "Impossível fazer essa rolagem"
            
          
    return f"{res} = {soma}"