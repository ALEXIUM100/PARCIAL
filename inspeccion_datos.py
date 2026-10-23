"""
inspeccion_datos.py
Inspección del inventario con Pandas: estructura, tipos de datos y estadísticas básicas.

Uso:
    python inspeccion_datos.py
"""
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


df = pd.read_csv("datos.csv", parse_dates=["ultimo_reabastecimiento"])

titulo("1. PRIMERAS Y ÚLTIMAS FILAS")
print(df.head())
print(df.tail(3))

titulo("2. DIMENSIONES (filas, columnas)")
print(df.shape)

titulo("3. ESTRUCTURA Y TIPOS DE DATOS (info)")
df.info()

titulo("4. TIPOS DE DATOS POR COLUMNA (dtypes)")
print(df.dtypes)

titulo("5. VALORES NULOS POR COLUMNA")
print(df.isnull().sum())

titulo("6. FILAS DUPLICADAS")
print(df.duplicated().sum())

titulo("7. ESTADÍSTICAS BÁSICAS NUMÉRICAS (describe)")
print(df.describe().round(2))

titulo("8. ESTADÍSTICAS DE COLUMNAS CATEGÓRICAS")
print(df[["id_producto", "producto", "categoria", "sucursal", "proveedor"]].describe())

titulo("9. VALORES ÚNICOS POR COLUMNA (nunique)")
print(df.nunique())

titulo("10. CONTEOS POR SUCURSAL Y CATEGORÍA")
print(df["sucursal"].value_counts())
print(df["categoria"].value_counts())

# Columnas calculadas útiles para el análisis
df["valor_inventario"] = df["stock"] * df["costo_unitario"]
df["margen_pct"] = (df["precio_venta"] - df["costo_unitario"]) / df["costo_unitario"] * 100

titulo("11. RESUMEN POR SUCURSAL")
resumen = df.groupby("sucursal").agg(
    registros=("producto", "count"),
    unidades=("stock", "sum"),
    valor_inventario=("valor_inventario", "sum"),
    margen_promedio=("margen_pct", "mean"),
).round(2)
print(resumen)

titulo("12. RESUMEN POR CATEGORÍA")
print(df.groupby("categoria").agg(
    unidades=("stock", "sum"),
    valor_inventario=("valor_inventario", "sum"),
    margen_promedio=("margen_pct", "mean"),
).round(2))

titulo("13. PRODUCTOS CON STOCK BAJO EL MÍNIMO")
bajo = df[df["stock"] < df["stock_minimo"]]
print(f"{len(bajo)} registros ({len(bajo) / len(df):.1%} del total)")
print(bajo.groupby("sucursal").size())
