import csv
import gzip

def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    extremos = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            letra = fila[0]
            valor = int(fila[1])
            if letra not in extremos:
                extremos[letra] = (valor, valor)
            else:
                maximo, minimo = extremos[letra]
                extremos[letra] = (max(maximo, valor), min(minimo, valor))
    return [(letra, maximo, minimo) for letra, (maximo, minimo) in sorted(extremos.items())]
