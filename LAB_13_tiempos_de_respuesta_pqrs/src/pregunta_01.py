from pathlib import Path
import pandas as pd

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    tablas = []
    for canal in ["letter", "web"]:
        ruta = "data/historical_requests_" + canal + ".csv.gz"
        tabla = pd.read_csv(ruta)
        tabla = tabla.drop_duplicates().copy()
        tabla["channel"] = canal
        tablas.append(tabla)
    datos = pd.concat(tablas, ignore_index=True)
    datos["in_date"] = pd.to_datetime(datos["in_date"], format="%Y-%m-%d")
    datos["out_date"] = pd.to_datetime(datos["out_date"], format="%Y-%m-%d")
    datos["year"] = datos["in_date"].dt.year
    datos["answered"] = datos["out_date"].notna()
    datos["pending"] = datos["out_date"].isna()
    datos["calendar_days"] = (datos["out_date"] - datos["in_date"]).dt.days

    def contar_dias_habiles(entrada, respuesta):
        if pd.isna(respuesta):
            return float("nan")
        dias = (respuesta - entrada).days
        semanas, restantes = divmod(dias, 7)
        habiles = semanas * 5
        # Excluimos la entrada e incluimos la respuesta, sin contar festivos.
        for paso in range(1, restantes + 1):
            dia_semana = (entrada.weekday() + paso) % 7
            if dia_semana < 5:
                habiles += 1
        return habiles

    dias_habiles = []
    for entrada, respuesta in zip(datos["in_date"], datos["out_date"]):
        dias_habiles.append(contar_dias_habiles(entrada, respuesta))
    datos["business_days"] = dias_habiles
    datos["on_time"] = datos["answered"] & (datos["business_days"] <= 15)

    # size cuenta también las solicitudes sin identificador.
    grupos = datos.groupby("channel")
    canales = pd.DataFrame({
        "requests": grupos.size(),
        "answered": grupos["answered"].sum(),
        "pending": grupos["pending"].sum(),
        "median_business_days": grupos["business_days"].median(),
        "on_time_rate": grupos["on_time"].mean(),
    })
    canales = canales.reset_index().sort_values("channel")

    grupos_anuales = datos.groupby(["year", "channel"])
    anuales = pd.DataFrame({
        "requests": grupos_anuales.size(),
        "pending": grupos_anuales["pending"].sum(),
        "on_time_rate": grupos_anuales["on_time"].mean(),
    })
    anuales = anuales.reset_index().sort_values(["year", "channel"])

    grupos_dias = datos.groupby("day_name")
    dias = pd.DataFrame({
        "requests": grupos_dias.size(),
        "median_calendar_days": grupos_dias["calendar_days"].median(),
        "median_business_days": grupos_dias["business_days"].median(),
    })
    orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dias = dias.reindex(orden_dias).reset_index()

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    canales.to_csv(carpeta_salida / "channel_summary.csv", index=False)
    anuales.to_csv(carpeta_salida / "yearly_summary.csv", index=False)
    dias.to_csv(carpeta_salida / "entry_day_summary.csv", index=False)
    return canales, anuales, dias
