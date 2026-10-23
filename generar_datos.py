"""
generar_datos.py
Genera el inventario (datos.csv) de una empresa salvadoreña con cinco sucursales:
San Salvador, Santa Ana, San Miguel, La Libertad y Sonsonate.

Uso:
    python generar_datos.py
"""
import numpy as np
import pandas as pd

SEMILLA = 42
rng = np.random.default_rng(SEMILLA)

SUCURSALES = ["San Salvador", "Santa Ana", "San Miguel", "La Libertad", "Sonsonate"]

# Peso de cada sucursal (San Salvador es la más grande)
PESO_SUCURSAL = {
    "San Salvador": 1.35,
    "Santa Ana": 1.00,
    "San Miguel": 1.00,
    "La Libertad": 0.90,
    "Sonsonate": 0.75,
}

# categoría -> (producto: (costo mín, costo máx) en USD, margen mínimo y máximo)
CATALOGO = {
    "Electrónica": (
        {"Televisor 43\"": (190, 320), "Audífonos Bluetooth": (8, 35), "Parlante portátil": (12, 45),
         "Cargador USB-C": (3, 9), "Tablet 10\"": (90, 180), "Smartwatch": (20, 60),
         "Cámara web HD": (10, 30)},
        (0.18, 0.35)),
    "Electrodomésticos": (
        {"Licuadora": (15, 35), "Cafetera": (14, 40), "Plancha de vapor": (10, 25),
         "Microondas": (60, 110), "Ventilador de pie": (18, 38), "Olla arrocera": (14, 30),
         "Freidora de aire": (35, 80)},
        (0.20, 0.38)),
    "Ropa y Calzado": (
        {"Camisa casual": (5, 12), "Pantalón de lona": (10, 22), "Zapatos deportivos": (20, 45),
         "Gorra": (2, 6), "Chumpa ligera": (12, 28), "Sandalias": (5, 14),
         "Uniforme escolar": (8, 18)},
        (0.40, 0.70)),
    "Hogar": (
        {"Juego de sábanas": (8, 20), "Almohada": (3, 9), "Set de ollas": (25, 60),
         "Cortinas": (6, 16), "Alfombra": (10, 35), "Organizador plástico": (2, 8),
         "Lámpara LED": (4, 12)},
        (0.30, 0.55)),
    "Papelería": (
        {"Cuaderno universitario": (0.8, 1.8), "Paquete de lapiceros": (1, 3), "Mochila escolar": (6, 18),
         "Calculadora": (4, 15), "Resma de papel": (3, 5.5), "Marcadores": (1.5, 4),
         "Folder con gancho": (0.3, 0.9)},
        (0.35, 0.60)),
    "Juguetes": (
        {"Carro a control remoto": (8, 25), "Muñeca": (4, 15), "Rompecabezas": (3, 10),
         "Set de bloques": (6, 30), "Pelota": (2, 8), "Juego de mesa": (7, 22),
         "Bicicleta infantil": (35, 70)},
        (0.35, 0.60)),
}

PROVEEDORES = ["Distribuidora Cuscatlán", "Importadora del Pacífico", "Comercial Centroamericana",
               "Tecno Import SV", "Grupo Maya", "Suministros La Unión"]

# Probabilidad de que cada sucursal tenga cada producto
filas = []
id_producto = 1000
for categoria, (productos, (mmin, mmax)) in CATALOGO.items():
    for producto, (cmin, cmax) in productos.items():
        id_producto += 1
        costo = round(float(rng.uniform(cmin, cmax)), 2)
        margen = float(rng.uniform(mmin, mmax))
        precio = round(costo * (1 + margen), 2)
        proveedor = str(rng.choice(PROVEEDORES))
        for sucursal in SUCURSALES:
            if rng.random() < 0.92:  # algunas sucursales no manejan todos los productos
                base = rng.integers(8, 120)
                stock = int(base * PESO_SUCURSAL[sucursal])
                # ~8% de los registros con stock crítico para análisis de reabastecimiento
                if rng.random() < 0.08:
                    stock = int(rng.integers(0, 6))
                stock_minimo = int(max(5, round(base * 0.2)))
                filas.append({
                    "id_producto": f"P{id_producto}",
                    "producto": producto,
                    "categoria": categoria,
                    "sucursal": sucursal,
                    "proveedor": proveedor,
                    "stock": stock,
                    "stock_minimo": stock_minimo,
                    "costo_unitario": costo,
                    "precio_venta": precio,
                })

df = pd.DataFrame(filas)

# Fecha del último reabastecimiento (últimos 120 días)
fechas = pd.Timestamp("2026-10-01") - pd.to_timedelta(rng.integers(0, 120, len(df)), unit="D")
df["ultimo_reabastecimiento"] = fechas.strftime("%Y-%m-%d")

df.to_csv("datos.csv", index=False, encoding="utf-8")
print(f"datos.csv generado: {df.shape[0]} filas x {df.shape[1]} columnas")
print(df.head())
