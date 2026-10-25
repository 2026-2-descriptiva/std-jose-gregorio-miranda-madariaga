from pathlib import Path
import pandas as pd

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    datos = pd.read_csv("data/superstore_orders.csv.gz", sep=";", decimal=",")
    datos["loss_line"] = datos["Profit"] < 0
    datos["lost_profit"] = -datos["Profit"].clip(upper=0)

    ventas = datos["Sales"].sum()
    utilidad = datos["Profit"].sum()
    resumen = pd.DataFrame([{
        "lines": len(datos),
        "orders": datos["Order ID"].nunique(),
        "sales": ventas,
        "profit": utilidad,
        "profit_margin": utilidad / ventas,
        "loss_lines": datos["loss_line"].sum(),
        "loss_line_rate": datos["loss_line"].mean(),
        "lost_profit": datos["lost_profit"].sum(),
    }])

    def clasificar_descuento(descuento):
        if descuento == 0:
            return "0%"
        if descuento <= 0.05:
            return "1%-5%"
        if descuento <= 0.10:
            return "6%-10%"
        return "más de 10%"

    datos["discount_band"] = datos["Discount"].apply(clasificar_descuento)
    descuentos = datos.groupby("discount_band").agg(
        lines=("Sales", "size"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        loss_line_rate=("loss_line", "mean"),
        lost_profit=("lost_profit", "sum"),
    )
    descuentos["profit_margin"] = descuentos["profit"] / descuentos["sales"]
    orden_descuentos = ["0%", "1%-5%", "6%-10%", "más de 10%"]
    descuentos = descuentos.reindex(orden_descuentos).reset_index()
    descuentos = descuentos[[
        "discount_band", "lines", "sales", "profit", "profit_margin",
        "loss_line_rate", "lost_profit",
    ]]

    segmentos = datos.groupby(["Customer Segment", "Product Category"]).agg(
        lines=("Sales", "size"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        lost_profit=("lost_profit", "sum"),
    )
    segmentos["profit_margin"] = segmentos["profit"] / segmentos["sales"]
    segmentos = segmentos.loc[segmentos["lines"] >= 100]
    segmentos = segmentos.sort_values("lost_profit", ascending=False).head(5)
    segmentos = segmentos.reset_index()
    segmentos = segmentos[[
        "Customer Segment", "Product Category", "lines", "sales", "profit",
        "profit_margin", "lost_profit",
    ]]

    carpeta_salida = Path("submission")
    carpeta_salida.mkdir(exist_ok=True)
    resumen.to_csv(carpeta_salida / "profitability_summary.csv", index=False)
    descuentos.to_csv(carpeta_salida / "discount_summary.csv", index=False)
    segmentos.to_csv(carpeta_salida / "priority_segments.csv", index=False)
    return resumen, descuentos, segmentos
