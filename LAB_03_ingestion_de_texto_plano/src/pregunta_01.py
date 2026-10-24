import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    registros = []
    registro_actual = None

    with open("data/clusters_report.txt", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue

            # Una fila nueva comienza con el número del clúster.
            if linea[0].isdigit():
                partes = linea.split(maxsplit=4)
                registro_actual = {
                    "cluster": int(partes[0]),
                    "cantidad_de_palabras_clave": int(partes[1]),
                    "porcentaje_de_palabras_clave": float(partes[2].replace(",", ".")),
                    "principales_palabras_clave": partes[4],
                }
                registros.append(registro_actual)
            elif registro_actual is not None:
                # Las líneas siguientes completan el texto del mismo clúster.
                registro_actual["principales_palabras_clave"] += " " + linea

    for registro in registros:
        texto = registro["principales_palabras_clave"]
        texto = " ".join(texto.split())
        texto = texto.removesuffix(".")

        palabras = []
        for palabra in texto.split(","):
            palabras.append(palabra.strip())
        registro["principales_palabras_clave"] = ", ".join(palabras)

    resultado = pd.DataFrame(registros)
    return resultado
