import csv
import gzip

def pregunta_10():
    """
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """

    resultado = []
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            letra = fila[0]
            cantidad_codes = len(fila[3].split(","))
            cantidad_metrics = len(fila[4].split(","))
            resultado.append((letra, cantidad_codes, cantidad_metrics))
    return resultado
