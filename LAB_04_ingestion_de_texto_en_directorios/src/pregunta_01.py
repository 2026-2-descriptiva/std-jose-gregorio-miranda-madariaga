from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)

    for division in ["train", "test"]:
        registros = []
        carpeta_division = Path("data") / division

        # El orden de las carpetas y los archivos se conserva en el CSV.
        for carpeta_sentimiento in sorted(carpeta_division.iterdir()):
            if not carpeta_sentimiento.is_dir():
                continue

            sentimiento = carpeta_sentimiento.name
            for ruta_archivo in sorted(carpeta_sentimiento.glob("*.txt")):
                with open(ruta_archivo, encoding="utf-8") as archivo:
                    frase = archivo.read().strip()

                registros.append({"phrase": frase, "target": sentimiento})

        dataset = pd.DataFrame(registros, columns=["phrase", "target"])
        ruta_salida = carpeta_salida / (division + "_dataset.csv")
        dataset.to_csv(ruta_salida, index=False, encoding="utf-8")
