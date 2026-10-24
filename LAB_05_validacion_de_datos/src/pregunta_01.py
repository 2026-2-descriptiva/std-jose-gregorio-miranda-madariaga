import json
from pathlib import Path
import pandas as pd

def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    tabla = pd.read_csv(
        "data/ventas.csv.gz",
        dtype=str,
        keep_default_na=False,
        na_values=["", "N/A"],
        encoding="utf-8-sig",
    )

    encabezados = []
    for columna in tabla.columns:
        nombre = columna.replace("\ufeff", "").strip().lower()
        nombre = "_".join(nombre.split())
        encabezados.append(nombre)
    tabla.columns = encabezados

    columnas_requeridas = [
        "supplier_id", "supplier", "country", "city", "purchase_date",
        "amount", "discount", "weight", "units", "unit_price", "contact_email",
    ]
    faltantes = sorted(set(columnas_requeridas) - set(tabla.columns))
    inesperadas = sorted(set(tabla.columns) - set(columnas_requeridas))

    valores_faltantes = {}
    for columna in tabla.columns:
        valores_faltantes[columna] = int(tabla[columna].isna().sum())

    # Solo convertimos una serie auxiliar para validar las unidades.
    unidades = pd.to_numeric(tabla["units"], errors="coerce")
    unidades_invalidas = unidades.notna() & (
        (unidades <= 0) | (unidades % 1 != 0)
    )
    correos_validos = tabla["contact_email"].str.fullmatch(
        r"[^@\s]+@[^@\s.]+(?:\.[^@\s.]+)+", na=False
    )

    reporte = {
        "row_count": int(tabla.shape[0]),
        "column_count": int(tabla.shape[1]),
        "missing_required_columns": faltantes,
        "unexpected_columns": inesperadas,
        "duplicate_row_count": int(tabla.duplicated().sum()),
        "duplicate_supplier_id_row_count": int(
            tabla["supplier_id"].duplicated(keep=False).sum()
        ),
        "missing_value_count_by_column": valores_faltantes,
        "invalid_email_count": int((~correos_validos).sum()),
        "invalid_unit_count": int(unidades_invalidas.sum()),
        "country_values": sorted(tabla["country"].dropna().unique().tolist()),
    }

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    ruta_reporte = carpeta_salida / "data_quality_report.json"
    with open(ruta_reporte, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, ensure_ascii=False, indent=4)

    return reporte
