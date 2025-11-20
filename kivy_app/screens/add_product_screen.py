from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from screens.topbar import TopBar
from screens.data_cache import cache
import os, json, shutil, platform, re

DEFAULT_IMAGE = 'assets/default_photo.png'

# --- INPUT MODERNO SIMPLE ---
class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configuración ultra-simple para garantizar texto visible
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (1, 1, 1, 1)  # Blanco
        self.foreground_color = (0, 0, 0, 1)  # Negro
        self.cursor_color = (0, 0, 1, 1)  # Azul
        self.selection_color = (0.5, 0.8, 1, 0.6)  # Azul claro
        self.font_size = 20
        self.bold = True
        self.padding = [10, 10]
        self.multiline = False

# --- BOTÓN MODERNO SIMPLE ---
class ModernButton(Button):
    def __init__(self, bg_color=(0.3, 0.6, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = bg_color
        self.color = (1, 1, 1, 1)
        self.font_size = 16
        self.bold = True

# --- SCREEN ---
class AddProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_image = DEFAULT_IMAGE
        self.build_interface()

    def clear_all_data(self):
        """Limpia todos los datos del formulario de agregar producto"""
        self.name_input.text = ''
        self.price_input.text = ''
        self.product_image = DEFAULT_IMAGE
        self.image_preview.source = DEFAULT_IMAGE
        self.feedback_label.text = ''
        print("🧹 AddProductScreen: Datos limpiados")

    def build_interface(self):
        # Fondo suave accesible
        with self.canvas.before:
            Color(0.97, 0.97, 0.99, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        main_layout = BoxLayout(orientation='vertical', spacing=10)
        main_layout.add_widget(TopBar(show_back=True))

        # Contenedor centrado con fondo transparente
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, None),
            height=500,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=25,
            padding=[30, 30, 30, 30]
        )
        # Sin fondo blanco - transparente

        # Título
        title_label = Label(
            text='Agregar producto',
            font_size=26,
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=40
        )
        form_container.add_widget(title_label)

        # Sección de nombre (ancho completo)
        name_section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=80)
        name_label = Label(
            text='Nombre del producto',
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=25,
            halign='left'
        )
        name_label.bind(texture_size=name_label.setter('text_size'))
        name_section.add_widget(name_label)
        
        self.name_input = ModernTextInput(
            hint_text='Nombre del producto',
            size_hint_y=None,
            height=50
        )
        name_section.add_widget(self.name_input)
        form_container.add_widget(name_section)

        # Sección horizontal: Precio + Imagen
        horizontal_section = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=200)
        
        # Precio (lado izquierdo)
        price_section = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.4)
        price_label = Label(
            text='Precio del producto',
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=25,
            halign='left'
        )
        price_label.bind(texture_size=price_label.setter('text_size'))
        price_section.add_widget(price_label)
        
        self.price_input = ModernTextInput(
            hint_text='0.00',
            size_hint_y=None,
            height=50,
            input_filter='float'
        )
        price_section.add_widget(self.price_input)
        price_section.add_widget(Widget())  # Espaciador
        
        horizontal_section.add_widget(price_section)
        
        # Imagen (lado derecho)
        image_section = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.6)
        img_label = Label(
            text='Imagen del producto',
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=25,
            halign='left'
        )
        img_label.bind(texture_size=img_label.setter('text_size'))
        image_section.add_widget(img_label)
        
        # Vista previa de imagen
        self.image_preview = Image(
            source=self.product_image,
            size_hint_y=None,
            height=120,
            allow_stretch=True,
            keep_ratio=True
        )
        image_section.add_widget(self.image_preview)
        
        # Botón seleccionar imagen
        select_image_btn = ModernButton(
            text='Seleccionar Imagen',
            size_hint_y=None,
            height=35,
            bg_color=(0.3, 0.6, 0.9, 1)
        )
        select_image_btn.bind(on_release=self.select_image)
        image_section.add_widget(select_image_btn)
        
        horizontal_section.add_widget(image_section)
        form_container.add_widget(horizontal_section)

        # Botones acción
        buttons_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=50)
        save_btn = ModernButton(text='Guardar', bg_color=(0.2, 0.7, 0.3, 1))
        cancel_btn = ModernButton(text='Cancelar', bg_color=(0.85, 0.3, 0.3, 1))
        save_btn.bind(on_press=self.save_product)
        cancel_btn.bind(on_press=self.cancel_action)
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        form_container.add_widget(buttons_layout)

        # Feedback
        self.feedback_label = Label(text='', font_size=15, color=(0.2, 0.6, 0.2, 1), size_hint_y=None, height=25)
        form_container.add_widget(self.feedback_label)

        main_layout.add_widget(Widget(size_hint_y=None, height=40))
        main_layout.add_widget(form_container)
        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def select_image(self, instance):
        """
        Seleccionar imagen del producto - OPTIMIZADO PARA WINDOWS
        
        Mejoras para compatibilidad con Windows:
        - Detección automática del sistema operativo
        - Ruta inicial en Pictures o Desktop en Windows
        - Soporte para más formatos de imagen (TIFF, WEBP)
        - Manejo mejorado de rutas con os.path.normpath()
        - Limpieza de caracteres especiales en nombres de archivo
        - Manejo robusto de errores con mensajes específicos
        """
        # Crear el file chooser - OPTIMIZADO PARA WINDOWS
        content = BoxLayout(orientation='vertical', spacing=10, padding=[10, 10])
        
        # Determinar la ruta inicial según el sistema operativo
        initial_path = os.path.expanduser('~')
        
        if platform.system() == 'Windows':
            # En Windows, intentar empezar en Pictures o Desktop
            pictures_path = os.path.join(os.path.expanduser('~'), 'Pictures')
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            
            if os.path.exists(pictures_path):
                initial_path = pictures_path
            elif os.path.exists(desktop_path):
                initial_path = desktop_path
            # Si no existen, usar home directory por defecto
        
        # File chooser - FileChooserListView es compatible con todas las plataformas
        # Agregamos más formatos de imagen para Windows
        filechooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.webp'],
            path=initial_path,
            size_hint_y=0.8  # Dar más espacio al file chooser
        )
        content.add_widget(filechooser)
        
        # Botones usando ModernButton para consistencia
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        select_btn = ModernButton(
            text='Seleccionar',
            bg_color=(0.2, 0.7, 0.3, 1)
        )
        cancel_btn = ModernButton(
            text='Cancelar',
            bg_color=(0.85, 0.3, 0.3, 1)
        )
        
        buttons_layout.add_widget(select_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        # Agregar información para el usuario
        info_label = Label(
            text='Selecciona una imagen (PNG, JPG, GIF, BMP, TIFF, WEBP)',
            size_hint_y=None,
            height=30,
            color=(0.3, 0.3, 0.3, 1),
            font_size=14
        )
        content.add_widget(info_label, index=len(content.children))  # Agregar al inicio
        
        # Crear popup
        popup = Popup(
            title='Seleccionar imagen del producto',
            content=content,
            size_hint=(0.9, 0.85),
            auto_dismiss=False
        )
        
        # Función para seleccionar imagen - MEJORADA PARA WINDOWS
        def select_image_file(instance):
            if filechooser.selection:
                selected_file = filechooser.selection[0]
                if self.is_valid_image(selected_file):
                    # Copiar imagen a la carpeta assets
                    self.copy_image_to_assets(selected_file)
                    popup.dismiss()
                else:
                    self.show_feedback("Por favor selecciona un archivo de imagen válido.", error=True)
            else:
                self.show_feedback("Por favor selecciona una imagen.", error=True)
        
        select_btn.bind(on_release=select_image_file)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()

    def is_valid_image(self, filepath):
        """Verificar si el archivo es una imagen válida - COMPATIBILIDAD WINDOWS"""
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp']
        return any(filepath.lower().endswith(ext) for ext in valid_extensions)

    def copy_image_to_assets(self, source_path):
        """Copiar imagen seleccionada a la carpeta assets - MEJORADO PARA WINDOWS"""
        try:
            # Normalizar la ruta de origen para Windows
            source_path = os.path.normpath(source_path)
            
            # Crear directorio assets si no existe - COMPATIBLE CON WINDOWS
            current_dir = os.getcwd()
            assets_dir = os.path.join(current_dir, 'assets')
            
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir, exist_ok=True)
                print(f"📁 Carpeta assets creada en: {assets_dir}")
            
            # Generar nombre único para la imagen con caracteres seguros para Windows
            filename = os.path.basename(source_path)
            # Limpiar caracteres especiales que pueden causar problemas en Windows
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            name, ext = os.path.splitext(filename)
            counter = 1
            new_filename = filename
            
            # Evitar sobrescribir archivos existentes
            while os.path.exists(os.path.join(assets_dir, new_filename)):
                new_filename = f"{name}_{counter}{ext}"
                counter += 1
            
            # Copiar archivo usando shutil con manejo de errores mejorado
            destination = os.path.join(assets_dir, new_filename)
            
            # Verificar que el archivo fuente existe y es legible
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"El archivo fuente no existe: {source_path}")
            
            if not os.access(source_path, os.R_OK):
                raise PermissionError(f"Sin permisos de lectura en el archivo: {source_path}")
            
            # Copiar archivo
            shutil.copy2(source_path, destination)
            
            # Verificar que la copia fue exitosa
            if not os.path.exists(destination):
                raise Exception("La copia del archivo falló")
            
            # Actualizar imagen del producto usando barra diagonal para Kivy
            self.product_image = f'assets/{new_filename}'
            self.image_preview.source = self.product_image
            
            self.show_feedback(f"✅ Imagen seleccionada: {new_filename}")
            print(f"📷 Imagen copiada exitosamente:")
            print(f"   Origen: {source_path}")
            print(f"   Destino: {destination}")
            
        except PermissionError as e:
            error_msg = "Error: Sin permisos para acceder a la imagen o carpeta"
            self.show_feedback(error_msg, error=True)
            print(f"❌ PermissionError: {e}")
        except FileNotFoundError as e:
            error_msg = "Error: Archivo de imagen no encontrado"
            self.show_feedback(error_msg, error=True)
            print(f"❌ FileNotFoundError: {e}")
        except OSError as e:
            error_msg = f"Error del sistema: {str(e)}"
            self.show_feedback(error_msg, error=True)
            print(f"❌ OSError: {e}")
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.show_feedback(error_msg, error=True)
            print(f"❌ Error detallado: {e}")
            import traceback
            traceback.print_exc()

    def save_product(self, instance):
        name = self.name_input.text.strip()
        price_text = self.price_input.text.strip()
        
        # Validaciones
        if not name or not price_text:
            self.show_feedback("Por favor, completa todos los campos.", error=True)
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                self.show_feedback("El precio debe ser mayor a 0.", error=True)
                return
        except ValueError:
            self.show_feedback("Precio inválido.", error=True)
            return

        # Cargar productos existentes usando cache optimizado
        products = cache.get_products()

        # Agregar nuevo producto
        new_product = {
            "name": name, 
            "price": str(price),  # Guardar como string para consistencia
            "image": self.product_image
        }
        products.append(new_product)
        
        # Guardar productos usando cache optimizado
        if cache.save_products(products):
            self.show_feedback(f'✅ Producto "{name}" agregado con éxito.')
            
            # El cache se actualiza automáticamente, no necesitamos recargar manualmente
            print("⚡ Producto agregado y cache actualizado automáticamente")
            
            # Limpiar formulario después de 2 segundos
            Clock.schedule_once(lambda dt: self.clear_form(), 2)
        else:
            self.show_feedback("Error al guardar producto", error=True)

    def clear_form(self):
        """Limpiar formulario"""
        self.name_input.text = ''
        self.price_input.text = ''
        self.product_image = DEFAULT_IMAGE
        self.image_preview.source = DEFAULT_IMAGE
        self.feedback_label.text = ''

    def show_feedback(self, message, error=False):
        """Mostrar mensaje de feedback"""
        self.feedback_label.text = message
        self.feedback_label.color = (0.85, 0.2, 0.2, 1) if error else (0.2, 0.6, 0.2, 1)
        Clock.schedule_once(lambda dt: setattr(self.feedback_label, 'text', ''), 4)

    def cancel_action(self, instance):
        """Cancelar y regresar"""
        self.clear_form()
        self.manager.current = 'product_list'

    def on_pre_enter(self, *args):
        """Limpiar formulario al entrar a la pantalla"""
        self.clear_form()