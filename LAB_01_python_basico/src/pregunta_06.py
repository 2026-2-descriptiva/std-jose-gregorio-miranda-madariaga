import csv
import gzip

def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """

    extremos = {}
    with gzip.open("data/data.csv.gz", "rt", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo, delimiter="\t"):
            for par in fila[4].split(","):
                clave, texto = par.split(":")
                valor = int(texto)
                if clave not in extremos:
                    extremos[clave] = (valor, valor)
                else:
                    minimo, maximo = extremos[clave]
                    extremos[clave] = (min(minimo, valor), max(maximo, valor))
    return [(clave, minimo, maximo) for clave, (minimo, maximo) in sorted(extremos.items())]
