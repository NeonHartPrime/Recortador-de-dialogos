import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext  
from tkinter import ttk
from PIL import Image, ImageTk
import keyboard  
import webbrowser  # Importar la librería webbrowser

class ImageCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recortador de Dialogos - Neon M - Neon Scan V1.0.7")

        self.modo_oscuro = False  # Inicia en modo claro

        # Frame principal
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para canvas y barra de desplazamiento vertical
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas para mostrar la imagen
        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de desplazamiento vertical
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de desplazamiento horizontal
        self.scrollbar_x = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Configurar el canvas para trabajar con ambas barras
        self.canvas.config(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.cut_images = []
        self.selected_regions = []
        self.original_image = None

        # Menú de opciones
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir Imagen", command=self.abrir_imagen)
        file_menu.add_command(label="Guardar Imagen Combinada", command=self.guardar_imagen)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Deshacer Último Recorte", command=self.deshacer_ultimo_recorte)

        file_menu.add_command(label="Salir", command=root.destroy)

        # Añadir el control de espaciado al menú superior
        opciones_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Opciones", menu=opciones_menu)
        # Modo claro/oscuro
        opciones_menu.add_command(label="Alternar Modo Oscuro", command=self.alternar_modo_oscuro)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ayuda", menu=help_menu)
        # Agregar una opción para abrir la web
        help_menu.add_command(label="Discord", command=self.abrir_sitio_web1)
        help_menu.add_command(label="Paypal", command=self.abrir_sitio_web2)

        # Frame para el control del espaciado
        self.frame_espaciado = tk.Frame(self.main_frame)
        self.frame_espaciado.pack(side=tk.TOP)

        # Etiqueta para el control de espaciado
        self.label_espacio = tk.Label(self.frame_espaciado, text="Espaciado entre recortes:")
        self.label_espacio.pack(side=tk.LEFT)

        # Control deslizante para ajustar el espaciado
        self.slider_espacio = ttk.Scale(self.frame_espaciado, from_=0, to=100, orient="horizontal", command=self.ajustar_espaciado)
        self.slider_espacio.set(20)
        self.slider_espacio.pack(side=tk.LEFT)

        # Atajos de teclado
        keyboard.add_hotkey("ctrl+o", self.abrir_imagen)
        keyboard.add_hotkey("ctrl+s", self.guardar_imagen)
        keyboard.add_hotkey("ctrl+z", self.deshacer_ultimo_recorte)
        keyboard.add_hotkey("ctrl+n", self.alternar_modo_oscuro)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        self.notas_texto = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=20, height=15)
        self.notas_texto.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Variables y notas iniciales
        self.espacio_entre_recortes = 20
        self.insertar_notas("Notas ver 1.0.7", "Aun está en fase beta y presenta varios bugs.")
        self.insertar_notas("Desarrollador", "Neon con M")
        self.insertar_notas("licencia", "Solo para el staff de Neon-Scan, si eres alguien mas pagame >:v")        
        self.insertar_notas("Adicional", "Leer el archivo leeme.txt para mas instrucciones o ayuda adicional.")

        # Aplicar modo claro por defecto
        self.aplicar_modo_claro()

    def abrir_imagen(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.cargar_imagen(file_path)

    def cargar_imagen(self, file_path):
        self.cut_images.clear()
        self.selected_regions.clear()
        image = Image.open(file_path)
        self.original_image = image.copy()
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

    def on_press(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.selection_start = (x, y)
        if hasattr(self, "selection_rect"):
            self.canvas.delete(self.selection_rect)
        self.selection_rect = None

    def on_drag(self, event):
        cur_x, cur_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            self.selection_start[0], self.selection_start[1], cur_x, cur_y, outline="red"
        )

    def on_release(self, event):
        end_x, end_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if self.selection_rect:
            x1, y1, x2, y2 = (
                min(self.selection_start[0], end_x),
                min(self.selection_start[1], end_y),
                max(self.selection_start[0], end_x),
                max(self.selection_start[1], end_y),
            )
            cropped_region = self.original_image.crop((x1, y1, x2, y2))
            self.selected_regions.insert(0, cropped_region)
            self.canvas.delete(self.selection_rect)
            self.mostrar_imagenes_recortadas()

    def mostrar_imagenes_recortadas(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        y_offset = 10
        for region in reversed(self.selected_regions):
            region_photo = ImageTk.PhotoImage(region)
            self.cut_images.append(region_photo)
            self.canvas.create_image(10, y_offset, anchor="nw", image=region_photo)
            y_offset += region.height + self.espacio_entre_recortes
        self.root.update()

    def guardar_imagen(self):
        if not self.selected_regions:
            messagebox.showwarning("Advertencia", "No hay regiones seleccionadas para guardar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Archivos PNG", "*.png")])
        if file_path:
            self.selected_regions.reverse()
            total_height = sum(region.height + self.espacio_entre_recortes for region in self.selected_regions) - self.espacio_entre_recortes
            nueva_imagen = Image.new("RGBA", (self.original_image.width, total_height), (100, 50, 0, 0))
            y_offset = 0
            for region in self.selected_regions:
                nueva_imagen.paste(region, (0, y_offset))
                y_offset += region.height + self.espacio_entre_recortes
            nueva_imagen.save(file_path)
            messagebox.showinfo("Éxito", "Las imágenes recortadas se han guardado exitosamente.")

    def deshacer_ultimo_recorte(self):
        if self.selected_regions:
            self.selected_regions.pop(0)
            self.mostrar_imagenes_recortadas()

    def on_mousewheel(self, event):
        if event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1, "units")

    def ajustar_espaciado(self, valor):
        self.espacio_entre_recortes = int(float(valor))
        self.mostrar_imagenes_recortadas()

    def alternar_modo_oscuro(self):
        if self.modo_oscuro:
            self.aplicar_modo_claro()
        else:
            self.aplicar_modo_oscuro()

    def aplicar_modo_oscuro(self):
        self.root.config(bg="#2E2E2E")
        self.canvas.config(bg="#2E2E2E")
        self.notas_texto.config(bg="#1C1C1C", fg="#F2F2F2", insertbackground="white")
        self.frame_espaciado.config(bg="#2E2E2E")
        self.label_espacio.config(bg="#2E2E2E", fg="white")
        self.modo_oscuro = True

    def aplicar_modo_claro(self):
        self.root.config(bg="white")
        self.canvas.config(bg="white")
        self.notas_texto.config(bg="white", fg="black", insertbackground="black")
        self.frame_espaciado.config(bg="white")
        self.label_espacio.config(bg="white", fg="black")
        self.modo_oscuro = False

    def insertar_notas(self, encabezado, contenido):
        self.notas_texto.configure(state=tk.NORMAL)
        self.notas_texto.insert(tk.END, f"{encabezado}\n", ('negrita',))
        self.notas_texto.insert(tk.END, f"{contenido}\n\n")
        self.notas_texto.configure(state=tk.DISABLED)

    def abrir_sitio_web1(self):
        # Redirigir a la página web especificada
        webbrowser.open("https://discord.gg/PDgEjNR7Wq")

    def abrir_sitio_web2(self):
        # Redirigir a la página web especificada
        webbrowser.open("https://paypal.me/neonscan?country.x=NI&locale.x=es_XC")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCutterApp(root)
    app.notas_texto.tag_configure('negrita', font=('Arial', 10, 'bold'))
    root.mainloop()
