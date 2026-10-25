from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    datos = pd.read_csv("data/sales.csv.gz")
    datos["OrderDate"] = pd.to_datetime(datos["OrderDate"])

    # Primera compra de cada cliente y mes de su cohorte.
    primeras_compras = datos.groupby("CustomerID")["OrderDate"].min()
    primeras_compras = primeras_compras.reset_index()
    primeras_compras = primeras_compras.rename(columns={"OrderDate": "first_order_date"})
    datos = pd.merge(datos, primeras_compras, on="CustomerID")
    datos["cohort_month"] = datos["first_order_date"].dt.strftime("%Y-%m")
    datos["period_index"] = (
        (datos["OrderDate"].dt.year - datos["first_order_date"].dt.year) * 12
        + datos["OrderDate"].dt.month - datos["first_order_date"].dt.month
    )

    retencion = datos.groupby(["cohort_month", "period_index"])["CustomerID"].nunique()
    retencion = retencion.reset_index(name="active_customers")
    tamanos = retencion[retencion["period_index"] == 0].copy()
    tamanos = tamanos[["cohort_month", "active_customers"]]
    tamanos = tamanos.rename(columns={"active_customers": "cohort_size"})
    retencion = pd.merge(retencion, tamanos, on="cohort_month")
    retencion["retention_rate"] = retencion["active_customers"] / retencion["cohort_size"]
    retencion = retencion.sort_values(["cohort_month", "period_index"])
    retencion = retencion.reset_index(drop=True)

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    retencion.to_csv(carpeta_salida / "cohort_retention.csv", index=False)

    # Pivot conserva como faltantes los períodos que no aparecen en la tabla.
    matriz = retencion.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    figura, eje = plt.subplots(figsize=(10, 6))
    imagen = eje.imshow(matriz, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    eje.set_xticks(range(len(matriz.columns)))
    eje.set_xticklabels(matriz.columns)
    eje.set_yticks(range(len(matriz.index)))
    eje.set_yticklabels(matriz.index)
    eje.set_xlabel("Meses desde la primera compra")
    eje.set_ylabel("Mes de la primera compra")
    eje.set_title("Retención de clientes por cohorte")

    for fila in range(len(matriz.index)):
        for columna in range(len(matriz.columns)):
            valor = matriz.iloc[fila, columna]
            if pd.notna(valor):
                color = "white" if valor >= 0.6 else "black"
                eje.text(columna, fila, f"{valor:.0%}", ha="center", va="center", color=color)

    barra = figura.colorbar(imagen, ax=eje)
    barra.set_label("Retención")
    barra.set_ticks([0, 0.25, 0.5, 0.75, 1])
    barra.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])
    figura.tight_layout()
    figura.savefig(carpeta_salida / "cohort_retention_heatmap.png", dpi=150)
    plt.close(figura)
    return retencion
