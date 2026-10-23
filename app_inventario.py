"""
app_inventario.py
Aplicación gráfica (PyQt5 + Matplotlib) para visualizar el inventario por sucursal.

Uso:
    python app_inventario.py
"""
import os
import sys

import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QVBoxLayout, QWidget,
)

RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos.csv")
TODAS = "Todas"
COLORES = ["#1f4e79", "#2e86c1", "#48c9b0", "#f5b041", "#e74c3c", "#8e44ad"]


class Grafico(QWidget):
    """Lienzo de Matplotlib con barra de herramientas."""

    def __init__(self):
        super().__init__()
        self.figura = Figure(figsize=(7, 4.5), tight_layout=True)
        self.canvas = FigureCanvas(self.figura)
        layout = QVBoxLayout(self)
        layout.addWidget(NavigationToolbar(self.canvas, self))
        layout.addWidget(self.canvas)

    def limpiar(self):
        self.figura.clear()
        return self.figura.add_subplot(111)

    def dibujar(self):
        self.canvas.draw()


class VentanaPrincipal(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Inventario por Sucursal - Consultoría de Datos")
        self.resize(1100, 720)
        self.df_original = df
        self.df = df

        central = QWidget()
        self.setCentralWidget(central)
        principal = QVBoxLayout(central)

        # ---- Filtros ----
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Sucursal:"))
        self.cmb_sucursal = QComboBox()
        filtros.addWidget(self.cmb_sucursal)
        filtros.addWidget(QLabel("Categoría:"))
        self.cmb_categoria = QComboBox()
        filtros.addWidget(self.cmb_categoria)
        btn_csv = QPushButton("Cargar otro CSV...")
        btn_csv.clicked.connect(self.cargar_csv)
        filtros.addWidget(btn_csv)
        filtros.addStretch()
        principal.addLayout(filtros)

        # ---- Indicadores ----
        self.lbl_kpi = QLabel()
        self.lbl_kpi.setAlignment(Qt.AlignCenter)
        self.lbl_kpi.setStyleSheet(
            "background:#eaf2f8; border:1px solid #aed6f1; border-radius:6px;"
            "padding:8px; font-size:14px; font-weight:bold; color:#1f4e79;")
        principal.addWidget(self.lbl_kpi)

        # ---- Pestañas con gráficos ----
        self.tabs = QTabWidget()
        principal.addWidget(self.tabs)
        self.g_unidades = Grafico()
        self.g_valor = Grafico()
        self.g_categoria = Grafico()
        self.g_margen = Grafico()
        self.g_critico = Grafico()
        self.tabla = QTableWidget()
        self.tabs.addTab(self.g_unidades, "Unidades por sucursal")
        self.tabs.addTab(self.g_valor, "Valor del inventario")
        self.tabs.addTab(self.g_categoria, "Distribución por categoría")
        self.tabs.addTab(self.g_margen, "Margen por categoría")
        self.tabs.addTab(self.g_critico, "Stock crítico")
        self.tabs.addTab(self.tabla, "Datos")

        self.cmb_sucursal.currentIndexChanged.connect(self.actualizar)
        self.cmb_categoria.currentIndexChanged.connect(self.actualizar)
        self.poblar_filtros()
        self.actualizar()

    # ------------------------------------------------------------------
    def poblar_filtros(self):
        for cmb, col in ((self.cmb_sucursal, "sucursal"), (self.cmb_categoria, "categoria")):
            cmb.blockSignals(True)
            cmb.clear()
            cmb.addItem(TODAS)
            cmb.addItems(sorted(self.df_original[col].unique()))
            cmb.blockSignals(False)

    def cargar_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV (*.csv)")
        if ruta:
            self.df_original = preparar(pd.read_csv(ruta))
            self.poblar_filtros()
            self.actualizar()

    def filtrar(self):
        df = self.df_original
        if self.cmb_sucursal.currentText() != TODAS:
            df = df[df["sucursal"] == self.cmb_sucursal.currentText()]
        if self.cmb_categoria.currentText() != TODAS:
            df = df[df["categoria"] == self.cmb_categoria.currentText()]
        return df

    # ------------------------------------------------------------------
    def actualizar(self):
        self.df = self.filtrar()
        df = self.df
        if df.empty:
            self.lbl_kpi.setText("Sin datos para el filtro seleccionado")
            return

        self.lbl_kpi.setText(
            f"Unidades: {df['stock'].sum():,}   |   "
            f"Valor del inventario: ${df['valor_inventario'].sum():,.2f}   |   "
            f"Margen promedio: {df['margen_pct'].mean():.1f}%   |   "
            f"Registros bajo el mínimo: {(df['stock'] < df['stock_minimo']).sum()}")

        self.graf_unidades()
        self.graf_valor()
        self.graf_categoria()
        self.graf_margen()
        self.graf_critico()
        self.llenar_tabla()

    def graf_unidades(self):
        ax = self.g_unidades.limpiar()
        datos = self.df.groupby("sucursal")["stock"].sum().sort_values(ascending=False)
        barras = ax.bar(datos.index, datos.values, color=COLORES[: len(datos)])
        ax.bar_label(barras, fmt="%d", padding=3)
        ax.set_title("Unidades en inventario por sucursal")
        ax.set_ylabel("Unidades")
        ax.tick_params(axis="x", rotation=15)
        self.g_unidades.dibujar()

    def graf_valor(self):
        ax = self.g_valor.limpiar()
        datos = self.df.groupby("sucursal")["valor_inventario"].sum().sort_values()
        barras = ax.barh(datos.index, datos.values, color=COLORES[1])
        ax.bar_label(barras, labels=[f"${v:,.0f}" for v in datos.values], padding=3)
        ax.set_title("Valor del inventario (a costo) por sucursal")
        ax.set_xlabel("USD")
        ax.margins(x=0.15)
        self.g_valor.dibujar()

    def graf_categoria(self):
        ax = self.g_categoria.limpiar()
        datos = self.df.groupby("categoria")["valor_inventario"].sum().sort_values(ascending=False)
        ax.pie(datos.values, labels=datos.index, autopct="%1.1f%%", startangle=90,
               colors=COLORES, wedgeprops={"edgecolor": "white"})
        ax.set_title("Participación en el valor del inventario por categoría")
        self.g_categoria.dibujar()

    def graf_margen(self):
        ax = self.g_margen.limpiar()
        datos = self.df.groupby("categoria")["margen_pct"].mean().sort_values()
        barras = ax.barh(datos.index, datos.values, color=COLORES[2])
        ax.bar_label(barras, fmt="%.1f%%", padding=3)
        ax.set_title("Margen de ganancia promedio por categoría")
        ax.set_xlabel("Margen sobre costo (%)")
        ax.margins(x=0.15)
        self.g_margen.dibujar()

    def graf_critico(self):
        ax = self.g_critico.limpiar()
        bajo = self.df[self.df["stock"] < self.df["stock_minimo"]]
        if bajo.empty:
            ax.text(0.5, 0.5, "No hay productos bajo el stock mínimo",
                    ha="center", va="center", fontsize=13)
            ax.axis("off")
        else:
            datos = bajo.groupby("sucursal").size().sort_values(ascending=False)
            barras = ax.bar(datos.index, datos.values, color=COLORES[4])
            ax.bar_label(barras, fmt="%d", padding=3)
            ax.set_title("Productos por debajo del stock mínimo, por sucursal")
            ax.set_ylabel("Cantidad de registros")
            ax.tick_params(axis="x", rotation=15)
        self.g_critico.dibujar()

    def llenar_tabla(self):
        cols = ["id_producto", "producto", "categoria", "sucursal", "stock",
                "stock_minimo", "costo_unitario", "precio_venta"]
        df = self.df[cols]
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        for i, fila in enumerate(df.itertuples(index=False)):
            for j, valor in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem(str(valor)))
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)


def preparar(df):
    df = df.copy()
    df["valor_inventario"] = df["stock"] * df["costo_unitario"]
    df["margen_pct"] = (df["precio_venta"] - df["costo_unitario"]) / df["costo_unitario"] * 100
    return df


def main():
    app = QApplication(sys.argv)
    try:
        df = preparar(pd.read_csv(RUTA_CSV))
    except FileNotFoundError:
        print("No se encontró datos.csv. Ejecuta primero: python generar_datos.py")
        sys.exit(1)
    ventana = VentanaPrincipal(df)
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
