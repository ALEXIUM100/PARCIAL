# Inventario por Sucursal – Consultoría de Datos

**Universidad Gerardo Barrios – Facultad de Ciencia y Tecnología**
**Asignatura:** Programación Computacional III – Parcial Segundo Cómputo

## Integrantes

- Deny Alexi Quintanilla Morataya
- Josue Ulises Zelaya Perdomo

## Descripción

Una empresa salvadoreña con cinco sucursales (San Salvador, Santa Ana, San Miguel, La Libertad y Sonsonate)
solicita un inventario consolidado y una aplicación gráfica para visualizarlo. Este proyecto entrega:

1. Un **inventario** en CSV (193 registros, 10 columnas) generado con Pandas/NumPy.
2. Un script de **inspección** con Pandas (estructura, tipos de datos y estadísticas básicas).
3. Una **aplicación gráfica en PyQt5** con gráficos de Matplotlib y filtros por sucursal y categoría.
4. Un **informe de consultoría en PDF** con portada, hallazgos, conclusiones por columna y recomendaciones.

## Estructura del repositorio

| Archivo | Descripción |
|---|---|
| `generar_datos.py` | Genera `datos.csv` (inventario simulado, semilla fija) |
| `inspeccion_datos.py` | Inspección con Pandas: `head`, `info`, `dtypes`, `describe`, nulos, duplicados, resúmenes |
| `app_inventario.py` | Aplicación PyQt5 + Matplotlib |
| `generar_informe.py` | Genera `informe_consultoria.pdf` a partir de los datos |
| `datos.csv` | Inventario (columnas: id_producto, producto, categoria, sucursal, proveedor, stock, stock_minimo, costo_unitario, precio_venta, ultimo_reabastecimiento) |
| `informe_consultoria.pdf` | Informe de consultoría |
| `requirements.txt` | Dependencias |

## Instalación y uso

```bash
# 1. (Opcional) crear entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar el inventario (ya incluido, solo si se quiere regenerar)
python generar_datos.py

# 4. Inspeccionar los datos con Pandas
python inspeccion_datos.py

# 5. Abrir la aplicación gráfica
python app_inventario.py

# 6. Regenerar el informe PDF (opcional)
python generar_informe.py
```

## Funciones de la aplicación

- Indicadores generales: unidades, valor del inventario, margen promedio y registros bajo el stock mínimo.
- Filtros por **sucursal** y **categoría**.
- Gráficos: unidades por sucursal, valor del inventario, distribución por categoría, margen por categoría y stock crítico.
- Pestaña con la tabla de datos y botón para cargar otro CSV.

## Nota

Los datos son simulados con fines académicos y no corresponden a una empresa real.
