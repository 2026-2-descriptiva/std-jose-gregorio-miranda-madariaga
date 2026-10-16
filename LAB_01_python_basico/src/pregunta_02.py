import csv
import gzip

def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """

    count = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            letra = fila[0]
            count[letra] = count.get(letra, 0) + 1
    return sorted(count.items())
