import csv
import gzip

def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """

    sumas = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            valor = int(fila[1])
            for letra in set(fila[3].split(",")):
                sumas[letra] = sumas.get(letra, 0) + valor
    return dict(sorted(sumas.items()))
