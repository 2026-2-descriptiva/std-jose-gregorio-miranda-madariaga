import csv
import gzip

def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    groups = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            letra = fila[0]
            valor = int(fila[1])
            if valor not in groups:
                groups[valor] = set()
            groups[valor].add(letra)
    return [(valor, sorted(groups[valor])) for valor in sorted(groups)]
