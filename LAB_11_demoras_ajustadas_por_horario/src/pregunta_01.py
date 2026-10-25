from pathlib import Path
import pandas as pd

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """

    datos = pd.read_csv("data/flights_by_carrier_day_hour.csv.gz")
    columnas_vuelos = ["operated_flights", "delayed_departure_15_flights"]

    # Suma de vuelos por hora y tasa nacional de demora.
    horarios = datos.groupby("scheduled_departure_hour")[columnas_vuelos].sum()
    horarios = horarios.reset_index()
    horarios = horarios.sort_values("scheduled_departure_hour")
    horarios["delay_rate"] = (
        horarios["delayed_departure_15_flights"] / horarios["operated_flights"]
    )

    # Unión de cada registro con la tasa nacional de su hora.
    tasas = horarios[["scheduled_departure_hour", "delay_rate"]]
    vuelos_con_tasas = pd.merge(
        datos, tasas, on="scheduled_departure_hour", how="left"
    )
    vuelos_con_tasas["expected_delayed_flights"] = (
        vuelos_con_tasas["operated_flights"] * vuelos_con_tasas["delay_rate"]
    )

    # Suma por aerolínea y selección de las que tienen suficiente volumen.
    columnas_sumar = columnas_vuelos + ["expected_delayed_flights"]
    aerolineas = vuelos_con_tasas.groupby("reporting_airline")[columnas_sumar].sum()
    aerolineas = aerolineas.reset_index()
    aerolineas = aerolineas[aerolineas["operated_flights"] >= 100000].copy()
    aerolineas["delay_rate"] = (
        aerolineas["delayed_departure_15_flights"] / aerolineas["operated_flights"]
    )
    aerolineas["observed_to_expected_ratio"] = (
        aerolineas["delayed_departure_15_flights"] / aerolineas["expected_delayed_flights"]
    )

    # La primera fila de cada ordenamiento corresponde a la peor aerolínea.
    ranking_sin_ajustar = aerolineas.sort_values("delay_rate", ascending=False)
    ranking_sin_ajustar = ranking_sin_ajustar.reset_index(drop=True)
    ranking_sin_ajustar["crude_rank"] = range(1, len(ranking_sin_ajustar) + 1)

    ranking_ajustado = aerolineas.sort_values("observed_to_expected_ratio", ascending=False)
    ranking_ajustado = ranking_ajustado.reset_index(drop=True)
    ranking_ajustado["adjusted_rank"] = range(1, len(ranking_ajustado) + 1)

    posiciones = ranking_sin_ajustar[["reporting_airline", "crude_rank"]]
    aerolineas = pd.merge(ranking_ajustado, posiciones, on="reporting_airline")
    aerolineas = aerolineas.sort_values("adjusted_rank")
    aerolineas = aerolineas[[
        "reporting_airline", "operated_flights", "delayed_departure_15_flights",
        "delay_rate", "expected_delayed_flights", "observed_to_expected_ratio",
        "crude_rank", "adjusted_rank",
    ]]

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    horarios.to_csv(carpeta_salida / "hourly_delay_rates.csv", index=False)
    aerolineas.to_csv(carpeta_salida / "carrier_adjusted_delays.csv", index=False)
    return horarios, aerolineas
