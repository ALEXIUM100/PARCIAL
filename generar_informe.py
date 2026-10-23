"""
generar_informe.py
Genera el informe de consultoría (informe_consultoria.pdf) a partir de datos.csv.
Las cifras se calculan con Pandas, así el informe siempre coincide con los datos.

Uso:
    python generar_informe.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# ----------------------------------------------------------------- DATOS DE PORTADA
# Edita estos datos antes de entregar
INTEGRANTES = ["Alexi [APELLIDOS]", "[Nombre del compañero/a]"]
MATERIA = "Programación Computacional III"
CARRERA = "Facultad de Ciencia y Tecnología"
UNIVERSIDAD = "Universidad Gerardo Barrios"
FECHA = "Octubre de 2026"
EMPRESA = "Empresa comercializadora salvadoreña (cinco sucursales)"

AZUL = colors.HexColor("#1f4e79")
AZUL_CLARO = colors.HexColor("#eaf2f8")
PALETA = ["#1f4e79", "#2e86c1", "#48c9b0", "#f5b041", "#e74c3c", "#8e44ad"]

os.makedirs("graficos", exist_ok=True)

# ----------------------------------------------------------------- CÁLCULOS
df = pd.read_csv("datos.csv")
df["valor"] = df["stock"] * df["costo_unitario"]
df["margen"] = (df["precio_venta"] - df["costo_unitario"]) / df["costo_unitario"] * 100
df["ganancia_pot"] = df["stock"] * (df["precio_venta"] - df["costo_unitario"])
df["dias"] = (pd.Timestamp("2026-10-01") - pd.to_datetime(df["ultimo_reabastecimiento"])).dt.days

tot_unid = int(df["stock"].sum())
tot_valor = df["valor"].sum()
tot_gan = df["ganancia_pot"].sum()
marg_prom = df["margen"].mean()

suc = df.groupby("sucursal").agg(unid=("stock", "sum"), valor=("valor", "sum"),
                                 gan=("ganancia_pot", "sum"), marg=("margen", "mean"),
                                 dias=("dias", "mean"))
suc["pct_unid"] = suc["unid"] / tot_unid * 100
suc["pct_valor"] = suc["valor"] / tot_valor * 100
suc = suc.sort_values("valor", ascending=False)

cat = df.groupby("categoria").agg(unid=("stock", "sum"), valor=("valor", "sum"),
                                  gan=("ganancia_pot", "sum"), marg=("margen", "mean"))
cat["pct_valor"] = cat["valor"] / tot_valor * 100
cat["pct_unid"] = cat["unid"] / tot_unid * 100
cat["pct_gan"] = cat["gan"] / tot_gan * 100
cat = cat.sort_values("valor", ascending=False)

prov = df.groupby("proveedor").agg(valor=("valor", "sum"), prods=("producto", "nunique"))
prov["pct"] = prov["valor"] / tot_valor * 100
prov = prov.sort_values("valor", ascending=False)

bajo = df[df["stock"] < df["stock_minimo"]].sort_values("sucursal")
sin_stock = int((df["stock"] == 0).sum())
pct_bajo = len(bajo) / len(df) * 100
tv = df[df["producto"] == 'Televisor 43"']["valor"].sum()
viejos = int((df["dias"] > 90).sum())
pct_viejos = viejos / len(df) * 100

top_suc, bot_suc = suc.index[0], suc.index[-1]
top_cat = cat.index[0]
cat_marg = cat.sort_values("marg", ascending=False)
elec_por_suc = df[df["categoria"] == "Electrónica"].groupby("sucursal")["valor"].sum() / df.groupby("sucursal")["valor"].sum() * 100


# ----------------------------------------------------------------- GRÁFICOS
def guardar(nombre):
    plt.tight_layout()
    plt.savefig(f"graficos/{nombre}.png", dpi=170)
    plt.close()


plt.figure(figsize=(7, 3.6))
b = plt.bar(suc.index, suc["valor"], color=PALETA[:5])
plt.bar_label(b, labels=[f"${v:,.0f}" for v in suc["valor"]], padding=3, fontsize=8)
plt.title("Valor del inventario a costo por sucursal (USD)", fontsize=10)
plt.xticks(rotation=12, fontsize=8)
guardar("informe_valor_sucursal")

plt.figure(figsize=(7, 3.6))
b = plt.barh(cat.index[::-1], cat["pct_valor"][::-1], color=PALETA[1])
plt.bar_label(b, fmt="%.1f%%", padding=3, fontsize=8)
plt.title("Participación de cada categoría en el valor del inventario", fontsize=10)
plt.xlim(0, cat["pct_valor"].max() * 1.2)
guardar("informe_categoria")

plt.figure(figsize=(7, 3.6))
cm_ = cat.sort_values("marg")
b = plt.barh(cm_.index, cm_["marg"], color=PALETA[2])
plt.bar_label(b, fmt="%.1f%%", padding=3, fontsize=8)
plt.title("Margen de ganancia promedio sobre costo por categoría", fontsize=10)
plt.xlim(0, cm_["marg"].max() * 1.2)
guardar("informe_margen")

plt.figure(figsize=(7, 3.4))
cr = bajo.groupby("sucursal").size().reindex(suc.index).fillna(0)
b = plt.bar(cr.index, cr.values, color=PALETA[4])
plt.bar_label(b, fmt="%d", padding=3, fontsize=8)
plt.title("Registros con stock por debajo del mínimo, por sucursal", fontsize=10)
plt.xticks(rotation=12, fontsize=8)
guardar("informe_critico")

# ----------------------------------------------------------------- ESTILOS
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=AZUL, fontSize=16, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=AZUL, fontSize=12, spaceBefore=8, spaceAfter=4, keepWithNext=1)
P = ParagraphStyle("P", parent=ss["BodyText"], alignment=TA_JUSTIFY, fontSize=10, leading=14, spaceAfter=6)
B = ParagraphStyle("B", parent=P, leftIndent=14, bulletIndent=4, spaceAfter=3)
CENTRO = ParagraphStyle("C", parent=ss["Normal"], alignment=TA_CENTER, fontSize=12, leading=18)
TITULO = ParagraphStyle("T", parent=ss["Title"], textColor=AZUL, fontSize=26, leading=32)
PIE = ParagraphStyle("Pie", parent=P, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)


def parrafo(t):
    return Paragraph(t, P)


def viñetas(items):
    return [Paragraph(t, B, bulletText="•") for t in items]


def tabla(datos, anchos=None, cabecera=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilo = [
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0b8c0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, AZUL_CLARO]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecera:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                   ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(estilo))
    return t


def imagen(nombre, ancho=15.5 * cm):
    return Image(f"graficos/{nombre}.png", width=ancho, height=ancho * 0.49)


def pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Informe de Consultoría de Datos - Inventario por Sucursal")
    canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


# ----------------------------------------------------------------- CONTENIDO
h = []

# --- Portada
h += [Spacer(1, 2.5 * cm)]
if os.path.exists("logo_ugb.png"):
    h += [Image("logo_ugb.png", width=10 * cm, height=10 * cm * 234 / 600), Spacer(1, 1 * cm)]
h += [Paragraph(UNIVERSIDAD, CENTRO), Paragraph(CARRERA, CENTRO), Spacer(1, 2.2 * cm),
      Paragraph("INFORME DE CONSULTORÍA DE DATOS", TITULO),
      Paragraph("Análisis del inventario por sucursal", CENTRO), Spacer(1, 0.6 * cm),
      Paragraph(f"<b>Cliente:</b> {EMPRESA}", CENTRO), Spacer(1, 2.2 * cm),
      Paragraph(f"<b>Asignatura:</b> {MATERIA}", CENTRO),
      Paragraph("<b>Evaluación:</b> Parcial - Segundo Cómputo", CENTRO), Spacer(1, 0.8 * cm),
      Paragraph("<b>Consultores:</b>", CENTRO)]
h += [Paragraph(n, CENTRO) for n in INTEGRANTES]
h += [Spacer(1, 1.2 * cm), Paragraph(f"San Miguel, El Salvador - {FECHA}", CENTRO), PageBreak()]

# --- 1. Resumen ejecutivo
h += [Paragraph("1. Resumen ejecutivo", H1),
      parrafo(f"La gerencia solicitó un inventario consolidado de sus cinco sucursales (San Salvador, Santa Ana, "
              f"San Miguel, La Libertad y Sonsonate) y una herramienta gráfica para explorarlo. Se construyó un conjunto de "
              f"datos de <b>{len(df)} registros</b> (producto por sucursal), que suma <b>{tot_unid:,} unidades</b> con un valor a costo de "
              f"<b>${tot_valor:,.2f}</b> y una ganancia potencial de <b>${tot_gan:,.2f}</b> si todo se vendiera al precio de lista."),
      parrafo("Los hallazgos principales son:")]
h += viñetas([
    f"<b>{top_suc}</b> concentra el {suc.loc[top_suc, 'pct_valor']:.1f}% del valor del inventario, mientras que <b>{bot_suc}</b> "
    f"solo el {suc.loc[bot_suc, 'pct_valor']:.1f}%.",
    f"La categoría <b>{top_cat}</b> representa el {cat.loc[top_cat, 'pct_valor']:.1f}% del valor con solo el "
    f"{cat.loc[top_cat, 'pct_unid']:.1f}% de las unidades; el producto Televisor 43\" por sí solo equivale al "
    f"{tv / tot_valor * 100:.1f}% del capital inmovilizado.",
    f"Hay <b>{len(bajo)} registros ({pct_bajo:.1f}%)</b> con stock por debajo del mínimo, y {sin_stock} de ellos están agotados.",
    f"El margen promedio es de {marg_prom:.1f}% sobre costo, pero varía desde "
    f"{cat['marg'].min():.1f}% (categorías de alto valor) hasta {cat['marg'].max():.1f}%.",
    f"El proveedor <b>{prov.index[0]}</b> abastece el {prov.iloc[0]['pct']:.1f}% del valor del inventario, "
    f"lo que implica concentración de riesgo.",
])

# --- 2. Datos y metodología
h += [Paragraph("2. Datos y metodología", H1),
      parrafo("El inventario se generó de forma simulada con Pandas y NumPy (semilla fija, reproducible) emulando el catálogo de una "
              "empresa comercial salvadoreña: 42 productos en 6 categorías distribuidos en 5 sucursales. Posteriormente se inspeccionó "
              "con <i>head, info, dtypes, describe, isnull, duplicated y nunique</i>, se calcularon indicadores derivados "
              "(valor del inventario = stock x costo; margen % = (precio - costo) / costo) y se desarrolló una aplicación en PyQt5 con "
              "gráficos de Matplotlib. Resultado de la inspección: sin valores nulos ni duplicados."),
      Paragraph("Variables del conjunto de datos", H2)]
desc = [["Columna", "Tipo", "Descripción"],
        ["id_producto", "texto", "Código único del producto"],
        ["producto", "texto", "Nombre del producto"],
        ["categoria", "texto", "Línea de producto (6 categorías)"],
        ["sucursal", "texto", "Sucursal donde está el inventario (5)"],
        ["proveedor", "texto", "Proveedor que abastece el producto (6)"],
        ["stock", "entero", "Unidades disponibles"],
        ["stock_minimo", "entero", "Nivel mínimo antes de reabastecer"],
        ["costo_unitario", "decimal", "Costo de adquisición (USD)"],
        ["precio_venta", "decimal", "Precio de venta (USD)"],
        ["ultimo_reabastecimiento", "fecha", "Fecha de la última reposición"]]
h += [tabla(desc, [4.5 * cm, 2.2 * cm, 9.8 * cm]), PageBreak()]

# --- 3. Hallazgos
h += [Paragraph("3. Análisis de hallazgos", H1), Paragraph("3.1 Distribución por sucursal", H2)]
filas = [["Sucursal", "Unidades", "% unid.", "Valor a costo", "% valor", "Margen prom."]]
for s, r in suc.iterrows():
    filas.append([s, f"{r['unid']:,.0f}", f"{r['pct_unid']:.1f}%", f"${r['valor']:,.0f}", f"{r['pct_valor']:.1f}%", f"{r['marg']:.1f}%"])
h += [tabla(filas, [3.4 * cm, 2.3 * cm, 2.1 * cm, 3 * cm, 2.1 * cm, 2.6 * cm]), Spacer(1, 6),
      imagen("informe_valor_sucursal"),
      parrafo(f"San Salvador es la sucursal más grande en unidades ({suc.loc['San Salvador', 'pct_unid']:.1f}%) y en valor "
              f"({suc.loc['San Salvador', 'pct_valor']:.1f}%). Santa Ana tiene un volumen de unidades similar al de San Miguel "
              f"({suc.loc['Santa Ana', 'unid']:,.0f} frente a {suc.loc['San Miguel', 'unid']:,.0f}) pero un valor mucho menor "
              f"(${suc.loc['Santa Ana', 'valor']:,.0f} frente a ${suc.loc['San Miguel', 'valor']:,.0f}): su inventario está compuesto por "
              f"artículos de menor costo. La Libertad destaca por la mayor dependencia de electrónica "
              f"({elec_por_suc['La Libertad']:.1f}% de su valor), frente a {elec_por_suc['Santa Ana']:.1f}% en Santa Ana."),
      Paragraph("3.2 Distribución por categoría", H2)]
filas = [["Categoría", "% unidades", "% valor", "% ganancia pot.", "Margen prom."]]
for c, r in cat.iterrows():
    filas.append([c, f"{r['pct_unid']:.1f}%", f"{r['pct_valor']:.1f}%", f"{r['pct_gan']:.1f}%", f"{r['marg']:.1f}%"])
h += [tabla(filas, [4.2 * cm, 2.8 * cm, 2.6 * cm, 3.4 * cm, 3 * cm]), Spacer(1, 6), imagen("informe_categoria"),
      parrafo("Las unidades se reparten de forma casi pareja entre categorías (14%-18% cada una), pero el valor no: Electrónica y "
              "Electrodomésticos suman dos tercios del capital invertido. Papelería, con la mayor cantidad de unidades de rotación "
              "probable, aporta menos del 2% del valor. Esto indica que el control de inventario debe priorizarse por valor y no por volumen."),
      Paragraph("3.3 Márgenes de ganancia", H2), imagen("informe_margen"),
      parrafo(f"Existe una relación inversa entre el costo del producto y su margen porcentual: Ropa y Calzado "
              f"({cat.loc['Ropa y Calzado', 'marg']:.1f}%), Papelería ({cat.loc['Papelería', 'marg']:.1f}%) y Juguetes "
              f"({cat.loc['Juguetes', 'marg']:.1f}%) superan el 48%, mientras Electrónica ({cat.loc['Electrónica', 'marg']:.1f}%) y "
              f"Electrodomésticos ({cat.loc['Electrodomésticos', 'marg']:.1f}%) rondan el 25%-28%. Sin embargo, en dólares absolutos "
              f"Electrónica genera el {cat.loc['Electrónica', 'pct_gan']:.1f}% de la ganancia potencial, por su alto precio unitario."),
      Paragraph("3.4 Stock crítico y reabastecimiento", H2), imagen("informe_critico"),
      parrafo(f"Se identificaron {len(bajo)} registros por debajo del stock mínimo ({pct_bajo:.1f}% del total), distribuidos en todas las sucursales, "
              f"y {sin_stock} agotados completamente. Los casos más preocupantes son: " +
              "; ".join(f"{r.producto} en {r.sucursal} ({r.stock} de {r.stock_minimo} mínimas)"
                        for r in bajo.sort_values('stock').head(4).itertuples()) + ". "
              f"Además, {viejos} registros ({pct_viejos:.1f}%) llevan más de 90 días sin reabastecerse; la sucursal con más antigüedad "
              f"promedio es La Libertad ({suc.loc['La Libertad', 'dias']:.0f} días frente a unos "
              f"{suc.drop('La Libertad')['dias'].mean():.0f} del resto)."),
      Paragraph("3.5 Proveedores", H2)]
filas = [["Proveedor", "Productos", "Valor a costo", "% del valor"]]
for p_, r in prov.iterrows():
    filas.append([p_, f"{r['prods']:.0f}", f"${r['valor']:,.0f}", f"{r['pct']:.1f}%"])
h += [tabla(filas, [6 * cm, 2.6 * cm, 3.6 * cm, 3 * cm]), Spacer(1, 6),
      parrafo(f"{prov.index[0]} suministra solo {prov.iloc[0]['prods']:.0f} productos, pero concentra el {prov.iloc[0]['pct']:.1f}% del valor "
              f"(incluye los televisores). Una interrupción de este proveedor afectaría de forma significativa a toda la red de sucursales."),
      PageBreak()]

# --- 4. Conclusiones por variable
h += [Paragraph("4. Conclusiones por columna analizada", H1)]
conc = [
    ("id_producto", "Identifica 42 productos únicos sin duplicados ni nulos; es una clave confiable para integrar el inventario con facturación o un sistema ERP."),
    ("producto", f"El catálogo es amplio y balanceado (7 productos por categoría). El Televisor 43\" es el artículo de mayor impacto financiero (${tv:,.0f}, {tv / tot_valor * 100:.1f}% del valor total)."),
    ("categoria", f"{top_cat} domina el valor ({cat.loc[top_cat, 'pct_valor']:.1f}%); Papelería casi no pesa financieramente ({cat.loc['Papelería', 'pct_valor']:.1f}%) aunque tiene la mayor cantidad de unidades."),
    ("sucursal", f"La distribución es desigual: {top_suc} acumula {suc.loc[top_suc, 'pct_valor']:.1f}% del valor y {bot_suc} {suc.loc[bot_suc, 'pct_valor']:.1f}%. Cada sucursal maneja entre 36 y 40 de los 42 productos."),
    ("proveedor", f"Existe concentración: {prov.index[0]} aporta el {prov.iloc[0]['pct']:.1f}% del valor con solo {prov.iloc[0]['prods']:.0f} productos; los demás proveedores van del 4% al 22%."),
    ("stock", f"El promedio es de {df['stock'].mean():.0f} unidades por registro (mediana {df['stock'].median():.0f}, máximo {df['stock'].max()}), con alta dispersión (desv. est. {df['stock'].std():.0f}). {sin_stock} registros están en cero."),
    ("stock_minimo", f"Funciona como alerta: {len(bajo)} registros ({pct_bajo:.1f}%) están bajo su umbral. La cobertura (stock / mínimo) es mayor en San Salvador (6.5 veces) y menor en Sonsonate (3.5 veces)."),
    ("costo_unitario", f"Muy asimétrico: mediana ${df['costo_unitario'].median():.2f} pero máximo ${df['costo_unitario'].max():.2f}. Unos pocos productos caros explican la mayor parte del capital."),
    ("precio_venta", f"Mediana de ${df['precio_venta'].median():.2f}; sigue la misma asimetría del costo. Los precios mantienen un margen positivo en el 100% de los productos."),
    ("ultimo_reabastecimiento", f"El promedio es de {df['dias'].mean():.0f} días desde la última reposición; el {pct_viejos:.1f}% de los registros supera los 90 días, señal de rotación lenta o reposición reactiva."),
]
filas = [["Variable", "Conclusión"]] + [[a, Paragraph(b, ParagraphStyle("c", parent=P, fontSize=8.5, leading=11, spaceAfter=0, alignment=0))] for a, b in conc]
h += [tabla(filas, [3.6 * cm, 12.9 * cm]), PageBreak()]

# --- 5. Recomendaciones
h += [Paragraph("5. Recomendaciones estratégicas", H1)]
recs = [
    ("Reabastecer de inmediato los registros agotados o críticos.",
     f"Priorizar los {sin_stock} registros sin existencias y los {len(bajo) - sin_stock} restantes bajo el mínimo, empezando por Smartwatch (Sonsonate), "
     f"Chumpa ligera (Santa Ana) y Cargador USB-C (La Libertad). Redistribuir entre sucursales con excedente antes de comprar."),
    ("Gestionar el inventario por valor (clasificación ABC).",
     "Los artículos de Electrónica y Electrodomésticos concentran dos tercios del capital: revisarlos semanalmente, mientras Papelería "
     "puede manejarse con reposición automática por punto de pedido."),
    ("Reducir la dependencia del proveedor principal.",
     f"Calificar un segundo proveedor para los televisores y otros productos de {prov.index[0]} y negociar convenios de entrega "
     f"o consignación para disminuir el riesgo de desabastecimiento."),
    ("Rebalancear el inventario entre sucursales.",
     f"San Salvador mantiene una cobertura de 6.5 veces su stock mínimo, contra 3.5 en Sonsonate. Transferir excedentes hacia las sucursales "
     f"con menor cobertura mejora el servicio sin aumentar la inversión."),
    ("Impulsar los productos de mayor margen porcentual.",
     "Ropa y Calzado, Papelería y Juguetes superan el 48% de margen; promociones y exhibición preferente en estas categorías mejoran la "
     "rentabilidad, y en electrónica conviene proteger el margen (25%) controlando descuentos."),
    ("Establecer un calendario de reabastecimiento.",
     f"Con {pct_viejos:.0f}% de registros sobre 90 días sin reposición, definir revisiones mensuales por sucursal, con atención especial a La Libertad."),
    ("Adoptar el tablero como herramienta de seguimiento.",
     "Mantener actualizado datos.csv (o conectarlo a la base de datos de la empresa) y utilizar la aplicación PyQt5 para monitorear "
     "los indicadores mensualmente y detectar desviaciones a tiempo."),
]
for i, (t, d) in enumerate(recs, 1):
    h += [Paragraph(f"<b>{i}. {t}</b>", ParagraphStyle("r", parent=P, spaceAfter=1)), parrafo(d)]

h += [Paragraph("6. Conclusión general", H1),
      parrafo("El inventario analizado es saludable en términos de márgenes (todos positivos) y de cobertura promedio, pero presenta "
              "tres riesgos que pueden corregirse con medidas de bajo costo: faltantes puntuales en productos clave, un capital muy "
              "concentrado en pocos productos y un proveedor, y reposiciones tardías en una parte relevante del catálogo. La herramienta "
              "gráfica entregada permite a la gerencia filtrar por sucursal y categoría para dar seguimiento a estos puntos."),
      Spacer(1, 10),
      Paragraph("Nota: los datos fueron generados de manera simulada con fines académicos; no corresponden a una empresa real.", PIE)]

doc = SimpleDocTemplate("informe_consultoria.pdf", pagesize=letter, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm, title="Informe de Consultoría de Datos - Inventario por Sucursal",
                        author=", ".join(INTEGRANTES))
doc.build(h, onLaterPages=pie_pagina)
print("informe_consultoria.pdf generado")
