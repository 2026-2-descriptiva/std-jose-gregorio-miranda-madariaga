from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    tabla = pd.read_csv("data/solicitudes_de_credito.csv.gz", sep=";", dtype=str)
    columnas = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "estrato",
        "comuna_ciudadano", "fecha_de_beneficio", "monto_del_credito", "línea_credito",
    ]
    tabla = tabla[columnas].copy()

    columnas_texto = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito",
    ]
    for columna in columnas_texto:
        texto = tabla[columna].str.lower()
        texto = texto.str.replace("_", " ", regex=False)
        texto = texto.str.replace("-", " ", regex=False)
        texto = texto.str.replace(r"\s+", " ", regex=True).str.strip()
        tabla[columna] = texto.replace("", pd.NA)

    # La comuna puede faltar; las demás columnas deben estar completas.
    columnas_obligatorias = []
    for columna in columnas:
        if columna != "comuna_ciudadano":
            columnas_obligatorias.append(columna)
    tabla = tabla.dropna(subset=columnas_obligatorias).copy()

    tabla["estrato"] = pd.to_numeric(tabla["estrato"]).astype(int)
    tabla["comuna_ciudadano"] = pd.to_numeric(tabla["comuna_ciudadano"])

    montos = tabla["monto_del_credito"].str.replace("$", "", regex=False)
    montos = montos.str.replace(",", "", regex=False).str.strip()
    tabla["monto_del_credito"] = pd.to_numeric(montos).astype(int)

    # Probamos los formatos del archivo sin confundir el día con el mes.
    fechas = pd.to_datetime(tabla["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce")
    for formato in ["%Y-%m-%d", "%Y/%m/%d"]:
        otras_fechas = pd.to_datetime(
            tabla["fecha_de_beneficio"], format=formato, errors="coerce"
        )
        fechas = fechas.fillna(otras_fechas)
    tabla["fecha_de_beneficio"] = fechas.dt.strftime("%Y-%m-%d")
    tabla = tabla.dropna(subset=columnas_obligatorias)

    # Los duplicados se eliminan después de unificar las representaciones.
    tabla = tabla.drop_duplicates()
    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    tabla.to_csv(carpeta_salida / "solicitudes_de_credito.csv", sep=";", index=False)
