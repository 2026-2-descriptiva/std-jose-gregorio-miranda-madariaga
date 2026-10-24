from pathlib import Path
import pandas as pd

def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """

    tablas = []
    for ruta_archivo in sorted(Path("data").glob("bank-marketing-campaing-*.csv.gz")):
        tabla = pd.read_csv(ruta_archivo)
        tablas.append(tabla)
    datos = pd.concat(tablas, ignore_index=True)
    datos = datos.sort_values("client_id").reset_index(drop=True)

    client = datos[[
        "client_id", "age", "job", "marital", "education",
        "credit_default", "mortgage",
    ]].copy()
    client["job"] = client["job"].str.replace(".", "", regex=False)
    client["job"] = client["job"].str.replace("-", "_", regex=False)
    client["education"] = client["education"].str.replace(".", "_", regex=False)
    client["education"] = client["education"].replace("unknown", pd.NA)
    for columna in ["credit_default", "mortgage"]:
        client[columna] = (client[columna] == "yes").astype(int)

    campaign = datos[[
        "client_id", "number_contacts", "contact_duration",
        "previous_campaign_contacts", "previous_outcome", "campaign_outcome",
    ]].copy()
    campaign["previous_outcome"] = (campaign["previous_outcome"] == "success").astype(int)
    campaign["campaign_outcome"] = (campaign["campaign_outcome"] == "yes").astype(int)

    # Usamos un diccionario para que los meses no dependan del idioma del equipo.
    meses = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    fechas = pd.to_datetime({
        "year": 2022,
        "month": datos["month"].map(meses),
        "day": datos["day"],
    })
    campaign["last_contact_date"] = fechas.dt.strftime("%Y-%m-%d")

    economics = datos[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    client.to_csv(carpeta_salida / "client.csv", index=False)
    campaign.to_csv(carpeta_salida / "campaign.csv", index=False)
    economics.to_csv(carpeta_salida / "economics.csv", index=False)

    return client, campaign, economics
