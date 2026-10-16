import csv
import gzip

def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.
    """

    counts = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            for par in fila[4].split(","):
                clave, _ = par.split(":")
                counts[clave] = counts.get(clave, 0) + 1

    return dict(sorted(counts.items()))
