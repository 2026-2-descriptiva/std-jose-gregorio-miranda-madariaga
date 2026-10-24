import json
from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    datos = pd.read_csv("data/insurance.csv.gz")
    identificadores_originales = ["age", "sex", "bmi", "children", "region"]
    tamanos_originales = datos.groupby(identificadores_originales).size()

    generalizados = datos.copy()
    generalizados["age_group"] = pd.cut(
        datos["age"], bins=[18, 30, 40, 50, 65], right=False,
        labels=["18-29", "30-39", "40-49", "50-64"],
    )
    generalizados["bmi_group"] = pd.cut(
        datos["bmi"], bins=[0, 18.5, 25, 30, float("inf")], right=False,
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
    )
    generalizados["children_group"] = pd.cut(
        datos["children"], bins=[0, 1, 3, float("inf")], right=False,
        labels=["0", "1-2", "3+"],
    )

    esquemas = {
        "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }
    resultados = {}
    tablas_publicadas = {}
    for nombre, columnas in esquemas.items():
        # observed=True cuenta solo las combinaciones que existen en los datos.
        grupos = generalizados.groupby(columnas, observed=True)
        tamanos = grupos.size()
        tamano_por_fila = grupos["smoker"].transform("size")
        publicados = generalizados.loc[tamano_por_fila >= 5].copy()

        grupos_publicados = publicados.groupby(columnas, observed=True)
        tamanos_publicados = grupos_publicados.size()
        diversidad = grupos_publicados["smoker"].nunique()
        sin_diversidad = diversidad == 1

        resultados[nombre] = {
            "quasi_identifiers": columnas,
            "equivalence_classes": int(len(tamanos)),
            "k_before_suppression": int(tamanos.min()),
            "suppressed_records": int((tamano_por_fila < 5).sum()),
            "published_records": int(len(publicados)),
            "published_classes": int(len(tamanos_publicados)),
            "classes_without_smoker_diversity": int(sin_diversidad.sum()),
            "records_without_smoker_diversity": int(tamanos_publicados[sin_diversidad].sum()),
        }
        tablas_publicadas[nombre] = publicados[columnas + ["smoker", "charges"]]

    seleccionado = min(
        resultados, key=lambda nombre: resultados[nombre]["suppressed_records"]
    )
    tabla_publicada = tablas_publicadas[seleccionado]
    reporte = {
        "original_k": int(tamanos_originales.min()),
        "original_unique_records": int((tamanos_originales == 1).sum()),
        "schemes": resultados,
        "selected_scheme": seleccionado,
        "mean_charges_original": float(datos["charges"].mean()),
        "mean_charges_published": float(tabla_publicada["charges"].mean()),
        "smoker_rate_original": float((datos["smoker"] == "yes").mean()),
        "smoker_rate_published": float((tabla_publicada["smoker"] == "yes").mean()),
    }

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    with open(carpeta_salida / "privacy_report.json", "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, ensure_ascii=False, indent=4)
    tabla_publicada.to_csv(carpeta_salida / "insurance_published.csv", index=False)
    return reporte
