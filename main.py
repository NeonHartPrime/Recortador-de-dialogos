import sys
import os 
import webbrowser  # Importar para abrir los enlaces web
from PyQt5.QtWidgets import QApplication, QMessageBox  ,QLabel, QMainWindow, QFileDialog, QScrollArea, QVBoxLayout, QPushButton, QWidget, QMenuBar, QAction, QSpinBox, QHBoxLayout, QSplitter, QComboBox, QToolBar
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QIcon  
from PyQt5.QtCore import Qt, QRect
from PIL import Image

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Establecer el icono de la ventana
        icon_path = os.path.join(os.path.dirname(__file__), 'data', 'iconv.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.image_label = QLabel(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)

        self.selection_rect = None
        self.start_point = None
        self.end_point = None
        self.is_selecting = False
        self.image = None

        self.selected_regions = []  # Almacena las regiones recortadas
        self.selection_rects = []  # Almacena los rectángulos de selección

        self.separation = 10  # Separación predeterminada entre recortes

        # Menú superior
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")

        save_action = QAction("Guardar Imagen Recortada", self)
        save_action.setShortcut("Ctrl+S")  # Atajo Ctrl + S        
        save_action.triggered.connect(self.save_cropped_image)
        file_menu.addAction(save_action)

        open_action = QAction("Abrir Imagen", self)
        open_action.setShortcut("Ctrl+O")  # Atajo Ctrl + O
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        undo_action = QAction("Deshacer Último Recorte", self)
        undo_action.setShortcut("Ctrl+Z")  # Atajo Ctrl + Z
        undo_action.triggered.connect(self.undo_last_crop)
        file_menu.addAction(undo_action)
        
        # Menú para enlaces web
        links_menu = menubar.addMenu("Enlaces")

        discord_action = QAction("Discord", self)
        discord_action.triggered.connect(lambda: self.open_link("https://discord.gg/fCBXrvmuXk"))
        links_menu.addAction(discord_action)

        github_action = QAction("GitHub", self)
        github_action.triggered.connect(lambda: self.open_link("https://github.com/NeonHartPrime"))
        links_menu.addAction(github_action)

        paypal_action = QAction("PayPal", self)
        paypal_action.triggered.connect(lambda: self.open_link("https://www.paypal.com/paypalme/neonscan?country.x=NI&locale.x=es_XC"))
        links_menu.addAction(paypal_action)

        # Crear una barra de herramientas para el selector de tema
        toolbar = QToolBar("Temas", self)
        self.addToolBar(toolbar)

        theme_selector = QComboBox(self)
        theme_selector.addItem("Modo default")
        theme_selector.addItem("Modo cyberpunk")
        theme_selector.addItem("Modo pastel")
        theme_selector.currentIndexChanged.connect(self.change_theme)
        toolbar.addWidget(theme_selector)

        # Layout para los botones
        button_layout = QHBoxLayout()

        open_btn = QPushButton('Abrir Imagen')
        open_btn.clicked.connect(self.open_image)
        button_layout.addWidget(open_btn)

        save_btn = QPushButton('Guardar Recortes')
        save_btn.clicked.connect(self.save_cropped_image)
        button_layout.addWidget(save_btn)

        undo_btn = QPushButton('Deshacer Último Recorte')
        undo_btn.clicked.connect(self.undo_last_crop)
        button_layout.addWidget(undo_btn)

        # Spinbox para ajustar la separación entre recortes
        self.sep_spinbox = QSpinBox()
        self.sep_spinbox.setRange(0, 1000)
        self.sep_spinbox.setValue(self.separation)
        self.sep_spinbox.setPrefix("Separación: ")
        self.sep_spinbox.valueChanged.connect(self.update_separation)
        button_layout.addWidget(self.sep_spinbox)

        # Layout principal
        main_layout = QHBoxLayout()  # Cambiar a QHBoxLayout para añadir el panel de notas

        left_layout = QVBoxLayout()
        left_layout.addLayout(button_layout)
        left_layout.addWidget(self.scroll_area)

        # Crear el panel de notas del desarrollador
        self.notes_label = QLabel("Notas del Desarrollador 2.7.0:\n\n"
                                  "- Este visor permite hacer selecciones y recortes.\n"
                                  "\n"
                                  "- Use los botones para guardar o deshacer recortes.\n"
                                  "\n"
                                  "- Puede ajustar la separación entre los recortes.\n"
                                  "\n"
                                  "- Pasa de ser una alfa a una beta\n"
                                  "\n"
                                  "- Desarrollado para el staff de Neon-Scan, si eres alguien mas pagame >:v\n"
                                  "\n"
                                  "- En el menú 'Enlaces' puede acceder a GitHub, Discord y PayPal.")
        self.notes_label.setWordWrap(True)  # Permitir que el texto se ajuste automáticamente
        self.notes_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Alinear el texto en la parte superior izquierda
        # Estilo en QSS, no lo establezcas aquí directamente
        # self.notes_label.setStyleSheet("background-color: #f0f0f0; padding: 10px;") 

        # Crear un área de desplazamiento para las notas en caso de que crezcan
        notes_scroll_area = QScrollArea()
        notes_scroll_area.setWidgetResizable(True)
        notes_scroll_area.setWidget(self.notes_label)

        # Añadir los layouts al QSplitter para dividir el área
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(notes_scroll_area)

        # Establecer el tamaño mínimo del área de notas a 120 px
        splitter.setSizes([800, 120])

        main_layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Cargar el estilo inicial
        self.load_style("theme_default.qss")

        self.setWindowTitle("Recortador de Dialogos - Neon M - Neon Scan")
        self.setGeometry(100, 100, 1000, 600)  # Ajustar el tamaño de la ventana

    def load_style(self, style_name):
        # Construir la ruta completa del archivo QSS
        style_path = os.path.join(os.path.dirname(__file__), 'data', style_name)
        with open(style_path, 'r') as file:
            style = file.read()
            self.setStyleSheet(style)


    def change_theme(self, index):
        if index == 0:
            self.load_style("theme_default.qss")  # Carga el estilo diurno
        elif index == 1:
            self.load_style("theme_cyberpunk.qss")   # Carga el estilo nocturno
        elif index == 2:
            self.load_style("theme_pastel.qss")   # Carga el estilo neón

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Imagen", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            self.image = QPixmap(file_name)
            self.image_label.setPixmap(self.image)
            self.image_label.adjustSize()

            # Convertir QPixmap a PIL Image para el recorte
            self.original_image = Image.open(file_name)

            # Limpiar las listas de recortes después de guardar
            self.selected_regions.clear()  # Eliminar todas las regiones recortadas
            self.selection_rects.clear()   # Eliminar todos los rectángulos de selección
            self.update()  # Actualizar la vista para reflejar los cambios

    def update_separation(self, value):
        self.separation = value
        self.update()  # Forzar la actualización de la vista

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image:
            self.start_point = self.image_label.mapFromParent(event.pos())
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.image:
            self.end_point = self.image_label.mapFromParent(event.pos())
            self.selection_rect = QRect(self.start_point.x() - 29, self.start_point.y() - 116, 
                                        self.end_point.x() - self.start_point.x(), 
                                        self.end_point.y() - self.start_point.y()).normalized()
            self.update()  # Asegúrate de que solo se llame si la selección ha cambiado


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            if self.selection_rect:
                self.create_cropped_image(self.selection_rect)
                self.selection_rects.append(self.selection_rect)
                self.selection_rect = None
            self.update()

    def create_cropped_image(self, rect):
        image_rect = self.image_label.pixmap().rect()
        corrected_rect = rect.intersected(image_rect)

        x1, y1 = corrected_rect.x(), corrected_rect.y()
        x2, y2 = corrected_rect.x() + corrected_rect.width(), corrected_rect.y() + corrected_rect.height()

        cropped_region = self.original_image.crop((x1, y1, x2, y2))
        self.selected_regions.append(cropped_region)

        self.update()

    def undo_last_crop(self):
        """Deshacer el último recorte realizado."""
        if self.selected_regions and self.selection_rects:
            self.selected_regions.pop()  # Eliminar la última región recortada
            self.selection_rects.pop()  # Eliminar el último rectángulo de selección
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.image_label.pixmap():
            return
    
        painter = QPainter(self.image_label.pixmap())
        painter.drawPixmap(0, 0, self.image)

        pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
        painter.setPen(pen)

        for rect in self.selection_rects:
            painter.drawRect(rect)

        y_offset = 10
        for region in self.selected_regions:
            region_qt_image = self.pil_to_qimage(region)
            region_pixmap = QPixmap.fromImage(region_qt_image)

            painter.drawPixmap(10, y_offset, region_pixmap)
            y_offset += region_pixmap.height() + self.separation  # Usamos la separación ajustable

        if self.selection_rect:
            painter.drawRect(self.selection_rect)

        painter.end()

    def pil_to_qimage(self, pil_image):
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        return qimage

    def save_cropped_image(self):
        if not self.selected_regions:
            return

        # Calcular el tamaño total de la imagen resultante
        total_height = sum(region.height for region in self.selected_regions) + (len(self.selected_regions) - 1) * self.separation
        max_width = max(region.width for region in self.selected_regions)

        # Crear una imagen nueva de tamaño suficiente para los recortes
        result_image = Image.new("RGBA", (max_width, total_height))

        # Colocar las imágenes una debajo de la otra con separación ajustable
        y_offset = 0
        for region in self.selected_regions:
            result_image.paste(region, (0, y_offset))
            y_offset += region.height + self.separation

        # Guardar la imagen resultante
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen Recortada", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if save_path:
            result_image.save(save_path)
            # Mostrar mensaje de confirmación
            QMessageBox.information(self, "Guardado", f"Imagen guardada con éxito!\nNúmero de recortes: {len(self.selected_regions)}")


    def open_link(self, url):
        """Abrir un enlace web en el navegador."""
        webbrowser.open(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Establecer el icono de la aplicación aquí
    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icon.ico')))  # Establecer el icono de la aplicación    
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
