# Importación de librerías necesarias para el funcionamiento del programa.
import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QCheckBox, QDialog, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import math

# Definición de la clase FilterWindow, que hereda de QDialog para crear una ventana de diálogo.
class FilterWindow(QDialog):
    def __init__(self, parent=None):
        super(FilterWindow, self).__init__(parent)  # Inicialización de la clase base.
        self.setWindowTitle('Filtros')  # Título de la ventana de filtros.
        self.setGeometry(200, 200, 400, 600)  # Configuración de la geometría de la ventana (posición x, y y dimensiones ancho, alto).

        layout = QVBoxLayout()  # Creación de un layout vertical para organizar widgets.

        # Creación de sliders con etiquetas mediante una función definida más adelante.
        self.create_slider_with_label(layout, "Min Population", 0, 36000, 0)
        self.create_slider_with_label(layout, "Max Population", 0, 36000, 36000)
        self.create_slider_with_label(layout, "Min Total Rooms", 0, 40000, 0)
        self.create_slider_with_label(layout, "Max Total Rooms", 0, 40000, 40000)
        self.create_slider_with_label(layout, "Min Median House Value", 0, 500100, 0)
        self.create_slider_with_label(layout, "Max Median House Value", 0, 500100, 500100)

        # Creación de checkboxes para seleccionar tipos de ubicaciones.
        self.inland_checkbox = QCheckBox("Inland")
        self.in_ocean_checkbox = QCheckBox("Menos de 1 hora del oceano")
        self.near_ocean_checkbox = QCheckBox("Near Ocean")
        self.near_bay_checkbox = QCheckBox("Near Bay")
        self.island_checkbox = QCheckBox("Island")

        # Adición de checkboxes al layout.
        layout.addWidget(self.inland_checkbox)
        layout.addWidget(self.in_ocean_checkbox)
        layout.addWidget(self.near_ocean_checkbox)
        layout.addWidget(self.near_bay_checkbox)
        layout.addWidget(self.island_checkbox)

        # Botón para aplicar los filtros y cerrar la ventana de diálogo.
        self.apply_button = QPushButton("Aplicar Filtros")
        self.apply_button.clicked.connect(self.accept)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)  # Establecimiento del layout en la ventana de diálogo.

    # Método para crear un slider y su etiqueta asociada.
    def create_slider_with_label(self, layout, title, min_val, max_val, init_val):
        label = QLabel(f"{title}: {init_val}")  # Creación de etiqueta con valor inicial.
        slider = QSlider(Qt.Horizontal)  # Creación de slider horizontal.
        slider.setMinimum(min_val)  # Establecimiento del valor mínimo.
        slider.setMaximum(max_val)  # Establecimiento del valor máximo.
        slider.setValue(init_val)  # Establecimiento del valor inicial.
        slider.valueChanged.connect(lambda value: label.setText(f"{title}: {value}"))  # Conexión del cambio de valor para actualizar la etiqueta.
        layout.addWidget(label)  # Adición de la etiqueta al layout.
        layout.addWidget(slider)  # Adición del slider al layout.
        setattr(self, f"{title.lower().replace(' ', '_')}_slider", slider)  # Almacenamiento del slider con un nombre accesible.
        setattr(self, f"{title.lower().replace(' ', '_')}_label", label)  # Almacenamiento de la etiqueta con un nombre accesible.

    def apply_filters(self):
        self.accept()  # Método para aceptar la acción y cerrar la ventana de diálogo.

# Definición de la clase principal GraphWindow que hereda de QMainWindow.
class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Grafo California')  # Título de la ventana principal.
        self.setGeometry(100, 100, 800, 600)  # Geometría de la ventana principal.

        self.central_widget = QWidget()  # Creación de un widget central.
        self.setCentralWidget(self.central_widget)  # Establecimiento del widget central.

        layout = QVBoxLayout()  # Creación de un layout vertical.
        self.central_widget.setLayout(layout)  # Asignación del layout al widget central.

        self.filter_button = QPushButton("Abrir Filtros")  # Botón para abrir la ventana de filtros.
        self.filter_button.clicked.connect(self.open_filter_window)  # Conexión del botón con la función para abrir la ventana de filtros.
        layout.addWidget(self.filter_button)  # Adición del botón al layout.

        self.figure, self.ax = plt.subplots()  # Creación de una figura y un eje con Matplotlib.
        self.canvas = FigureCanvas(self.figure)  # Creación de un canvas para la figura.
        layout.addWidget(self.canvas)  # Adición del canvas al layout.

        self.addToolBar(Qt.BottomToolBarArea, NavigationToolbar(self.canvas, self))  # Adición de una barra de herramientas para la navegación del gráfico.

        self.data = pd.read_csv('housing.csv')  # Carga de datos desde un archivo CSV.
        self.G = nx.Graph()  # Creación de un grafo vacío con NetworkX.
        self.node_positions = {}  # Diccionario para almacenar las posiciones de los nodos.
        self.background_image = plt.imread('h.jpeg')  # Carga de una imagen de fondo.

        self.reset_filters_button = QPushButton("Reiniciar Filtros")  # Botón para reiniciar los filtros a sus valores por defecto.
        self.reset_filters_button.clicked.connect(self.reset_filters)  # Conexión del botón con la función para resetear filtros.
        layout.addWidget(self.reset_filters_button)  # Adición del botón al layout.

        self.add_nodes()  # Llamada al método para añadir nodos al grafo.
        self.draw_graph()  # Llamada al método para dibujar el grafo.
        self.show()  # Método para mostrar la ventana.

        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)  # Conexión del evento de movimiento del ratón para interactuar con el grafo.

    # Método para resetear los filtros.
    def reset_filters(self):
        if hasattr(self, 'filter_window'):
            self.filter_window.min_population_slider.setValue(0)
            self.filter_window.max_population_slider.setValue(36000)
            self.filter_window.min_total_rooms_slider.setValue(0)
            self.filter_window.max_total_rooms_slider.setValue(40000)
            self.filter_window.min_median_house_value_slider.setValue(0)
            self.filter_window.max_median_house_value_slider.setValue(500100)
            self.filter_window.inland_checkbox.setChecked(False)
            self.filter_window.in_ocean_checkbox.setChecked(False)
            self.filter_window.near_ocean_checkbox.setChecked(False)
            self.filter_window.near_bay_checkbox.setChecked(False)
            self.filter_window.island_checkbox.setChecked(False)
            self.draw_graph()  # Redibujar el grafo con los filtros reiniciados.

    # Método para manejar eventos de movimiento del ratón sobre el grafo.
    def on_mouse_move(self, event):
        if event.inaxes == self.ax:  # Verificar que el movimiento sea dentro del área del gráfico.
            x, y = event.xdata, event.ydata  # Obtención de las coordenadas del ratón.
            closest_node, min_dist = None, float('inf')
            for node, (node_x, node_y) in self.node_positions.items():  # Iteración sobre las posiciones de los nodos.
                dist = (node_x - x) ** 2 + (node_y - y) ** 2  # Cálculo de la distancia cuadrada.
                if dist < min_dist:
                    closest_node, min_dist = node, dist  # Actualización del nodo más cercano y la distancia mínima.
            if closest_node is not None and min_dist < 0.01:  # Comprobación de un umbral para decidir si mostrar un tooltip.
                node_data = self.G.nodes[closest_node]  # Obtención de datos del nodo más cercano.
                tooltip_text = f"ID: {closest_node}\nPopulation: {node_data['population']}\nTotal Rooms: {node_data['total_rooms']}\nMedian House Value: {node_data['median_house_value']}\nOcean Proximity: {node_data['ocean_proximity']}"
                self.ax.set_title(tooltip_text, fontsize=10)  # Mostrar los datos del nodo como título del gráfico.
            else:
                self.ax.set_title('Grafo California')  # Mostrar título predeterminado si no hay nodo cercano.
            self.canvas.draw_idle()  # Redibujar el gráfico para actualizar el título.

    # Método para aplicar los filtros seleccionados en la ventana de filtros.
    def apply_filters(self, filter_window):
        # Obtención de los valores de los sliders y checkboxes.
        min_population = filter_window.min_population_slider.value()
        max_population = filter_window.max_population_slider.value()
        min_total_rooms = filter_window.min_total_rooms_slider.value()
        max_total_rooms = filter_window.max_total_rooms_slider.value()
        min_median_house_value = filter_window.min_median_house_value_slider.value()
        max_median_house_value = filter_window.max_median_house_value_slider.value()
        inland = filter_window.inland_checkbox.isChecked()
        in_ocean = filter_window.in_ocean_checkbox.isChecked()
        near_ocean = filter_window.near_ocean_checkbox.isChecked()
        near_bay = filter_window.near_bay_checkbox.isChecked()
        island = filter_window.island_checkbox.isChecked()

        filtered_nodes = []  # Lista para almacenar nodos que cumplen con los filtros.
        for node in self.G.nodes:  # Iteración sobre los nodos del grafo.
            node_data = self.G.nodes[node]  # Obtención de datos del nodo.
            # Comprobaciones de los filtros de valor de vivienda, población, y habitaciones.
            median_house_value_cond = node_data['median_house_value'] >= min_median_house_value and node_data['median_house_value'] <= max_median_house_value
            if (min_population <= node_data['population'] <= max_population and
                min_total_rooms <= node_data['total_rooms'] <= max_total_rooms and
                median_house_value_cond):
                ocean_proximity_cond = (inland and node_data['ocean_proximity'] == 'INLAND') or \
                                    (in_ocean and node_data['ocean_proximity'] == '<1H OCEAN') or \
                                    (near_ocean and node_data['ocean_proximity'] == 'NEAR OCEAN') or \
                                    (near_bay and node_data['ocean_proximity'] == 'NEAR BAY') or \
                                    (island and node_data['ocean_proximity'] == 'ISLAND') or \
                                    not (inland or in_ocean or near_ocean or near_bay or island)
                if ocean_proximity_cond:
                    filtered_nodes.append(node)  # Adición del nodo a la lista de nodos filtrados si cumple con todos los filtros.

        self.draw_filtered_graph(filtered_nodes)  # Llamada al método para dibujar el grafo con los nodos filtrados.

    # Método para dibujar el grafo con los nodos filtrados.
    def draw_filtered_graph(self, filtered_nodes):
        self.ax.clear()  # Limpieza del área de dibujo del gráfico.
        self.ax.imshow(self.background_image, extent=[-125, -113, 32, 43], aspect='auto')  # Colocación de la imagen de fondo.

        # Agrupación de nodos por proximidad al océano.
        proximity_groups = {}
        for node in filtered_nodes:
            proximity = self.G.nodes[node]['ocean_proximity']
            if proximity not in proximity_groups:
                proximity_groups[proximity] = []
            proximity_groups[proximity].append(node)

        # Dibujo de nodos y conexiones dentro de cada grupo de proximidad.
        for proximity, nodes in proximity_groups.items():
            sorted_nodes = sorted(nodes, key=lambda node: self.G.nodes[node]['longitude'])  # Ordenación de nodos dentro del grupo por longitud.
            group_positions = {node: self.node_positions[node] for node in sorted_nodes}  # Obtención de posiciones de nodos ordenados.
            nx.draw_networkx_nodes(self.G, group_positions, nodelist=sorted_nodes, node_size=20, node_color='blue', ax=self.ax)  # Dibujo de nodos.

            # Conexión de nodos secuencialmente.
            for i in range(len(sorted_nodes) - 1):
                node1, node2 = sorted_nodes[i], sorted_nodes[i + 1]
                self.ax.plot([self.node_positions[node1][0], self.node_positions[node2][0]],
                            [self.node_positions[node1][1], self.node_positions[node2][1]], color='gray')

        self.ax.axis('off')  # Ocultación de los ejes.
        self.canvas.draw()  # Redibujado del gráfico.

    # Método para añadir nodos al grafo basándose en los datos del archivo CSV.
    def add_nodes(self):
        for index, row in self.data.iterrows():  # Iteración sobre las filas del DataFrame.
            self.G.add_node(index,
                            longitude=row['longitude'],
                            latitude=row['latitude'],
                            population=row['population'],
                            total_rooms=row['total_rooms'],
                            median_house_value=row['median_house_value'],
                            ocean_proximity=row['ocean_proximity'])  # Adición de un nodo al grafo con los datos correspondientes.

            self.node_positions[index] = (row['longitude'], row['latitude'])  # Almacenamiento de la posición geográfica del nodo.

    # Método para dibujar el grafo inicial.
    def draw_graph(self):
        self.ax.clear()  # Limpieza del área de dibujo.
        self.ax.imshow(self.background_image, extent=[-125, -113, 32, 43], aspect='auto')  # Colocación de la imagen de fondo.
        nx.draw_networkx_nodes(self.G, self.node_positions, node_size=20, node_color='blue', ax=self.ax)  # Dibujo de los nodos en el gráfico.
        self.ax.axis('off')  # Ocultación de los ejes.
        self.ax.set_title('Grafo California')  # Establecimiento del título del gráfico.
        self.canvas.draw()  # Redibujado del gráfico.

    # Método para abrir la ventana de filtros y aplicar los filtros si se aceptan.
    def open_filter_window(self):
        self.filter_window = FilterWindow(self)  # Creación de la ventana de filtros.
        if self.filter_window.exec_():  # Mostrar la ventana de filtros como un diálogo modal y comprobar si se aceptó.
            self.apply_filters(self.filter_window)  # Aplicación de los filtros seleccionados.

# Punto de entrada principal del programa.
if __name__ == '__main__':
    app = QApplication(sys.argv)  # Inicialización de la aplicación PyQt.
    window = GraphWindow()  # Creación de la ventana principal.
    sys.exit(app.exec_())  # Ejecución de la aplicación y salida.
