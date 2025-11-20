from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp
from screens.topbar import TopBar
from screens.data_cache import cache
import csv
import os
from datetime import datetime

# --- BOTÓN MODERNO SIMPLE ---
class ModernButton(Button):
    def __init__(self, bg_color=(0.3, 0.6, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = bg_color
        self.color = (1, 1, 1, 1)
        self.font_size = dp(12)
        self.bold = True

class CajaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saldo_actual = 0.0
        self.build_interface()

    def cargar_saldo(self):
        """Cargar saldo actual usando cache optimizado"""
        return cache.get_saldo()

    def guardar_saldo(self, saldo):
        """Guardar saldo actual usando cache optimizado"""
        return cache.save_saldo(saldo)

    def build_interface(self):
        # Cargar saldo al construir la interfaz
        self.saldo_actual = self.cargar_saldo()
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        main_layout.add_widget(TopBar(show_back=True))

        # Contenedor principal
        content_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.95, None),
            height=dp(650),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(15),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )

        # Título y saldo (parte superior)
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )

        title_label = Label(
            text='CAJA',
            font_size=dp(24),
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )
        header_layout.add_widget(title_label)

        self.saldo_label = Label(
            text=f'${self.saldo_actual:.2f}',
            font_size=dp(32),
            color=(0.1, 0.6, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(55)
        )
        header_layout.add_widget(self.saldo_label)

        desc_label = Label(
            text='Dinero en caja',
            font_size=dp(13),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20)
        )
        header_layout.add_widget(desc_label)

        content_container.add_widget(header_layout)

        # Layout de dos columnas - REDUCIDO
        columns_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(280)  # Reducido de 350 a 280
        )

        # COLUMNA IZQUIERDA: AGREGAR DINERO - REDUCIDA
        left_column = BoxLayout(
            orientation='vertical',
            spacing=dp(8),  # Reducido de 10 a 8
            size_hint=(0.5, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)]  # Padding interno reducido
        )

        # Fondo verde claro para columna izquierda - MÁS SUTIL
        with left_column.canvas.before:
            Color(0.95, 0.98, 0.95, 1)  # Verde mucho más claro
            self._left_bg = Rectangle(pos=left_column.pos, size=left_column.size)
            Color(0.2, 0.7, 0.3, 0.2)  # Borde verde más sutil
            self._left_border = Rectangle(pos=left_column.pos, size=left_column.size)

        def update_left_bg(*args):
            self._left_bg.pos = left_column.pos
            self._left_bg.size = left_column.size
            self._left_border.pos = left_column.pos
            self._left_border.size = left_column.size

        left_column.bind(pos=update_left_bg, size=update_left_bg)

        # Título columna izquierda - REDUCIDO
        left_title = Label(
            text='AGREGAR DINERO',
            font_size=dp(12),  # Reducido de 14 a 12
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(25)  # Reducido de 30 a 25
        )
        left_column.add_widget(left_title)

        # Descripción - REDUCIDA
        left_desc = Label(
            text='Ingresar dinero manualmente a la caja',
            font_size=dp(10),  # Reducido de 11 a 10
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20)  # Reducido de 25 a 20
        )
        left_column.add_widget(left_desc)

        # Input para agregar - REDUCIDO
        self.dinero_input = TextInput(
            hint_text='Cantidad (ej: 100.50)',
            font_size=dp(12),  # Reducido de 14 a 12
            size_hint_y=None,
            height=dp(30),  # Reducido de 35 a 30
            multiline=False,
            input_filter='float'
        )
        left_column.add_widget(self.dinero_input)

        # Botón agregar - REDUCIDO
        agregar_btn = ModernButton(
            text='AGREGAR',
            bg_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=None,
            height=dp(35)  # Reducido de 40 a 35
        )
        agregar_btn.bind(on_press=self.agregar_dinero_manual)
        left_column.add_widget(agregar_btn)

        # Espaciador
        left_column.add_widget(Widget())

        columns_layout.add_widget(left_column)

        # COLUMNA DERECHA: ENTREGAR DINERO - REDUCIDA
        right_column = BoxLayout(
            orientation='vertical',
            spacing=dp(8),  # Reducido de 10 a 8
            size_hint=(0.5, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)]  # Padding interno reducido
        )

        # Fondo rojo claro para columna derecha - MÁS SUTIL
        with right_column.canvas.before:
            Color(0.98, 0.95, 0.95, 1)  # Rojo mucho más claro
            self._right_bg = Rectangle(pos=right_column.pos, size=right_column.size)
            Color(0.8, 0.3, 0.3, 0.2)  # Borde rojo más sutil
            self._right_border = Rectangle(pos=right_column.pos, size=right_column.size)

        def update_right_bg(*args):
            self._right_bg.pos = right_column.pos
            self._right_bg.size = right_column.size
            self._right_border.pos = right_column.pos
            self._right_border.size = right_column.size

        right_column.bind(pos=update_right_bg, size=update_right_bg)

        # Título columna derecha - REDUCIDO
        right_title = Label(
            text='ENTREGAR DINERO',
            font_size=dp(12),  # Reducido de 14 a 12
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(25)  # Reducido de 30 a 25
        )
        right_column.add_widget(right_title)

        # Descripción - REDUCIDA
        right_desc = Label(
            text='Entregar dinero a la tesorera',
            font_size=dp(10),  # Reducido de 11 a 10
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(20)  # Reducido de 25 a 20
        )
        right_column.add_widget(right_desc)

        # Input para entregar - REDUCIDO
        self.entregar_input = TextInput(
            hint_text='Cantidad (ej: 200.00)',
            font_size=dp(12),  # Reducido de 14 a 12
            size_hint_y=None,
            height=dp(30),  # Reducido de 35 a 30
            multiline=False,
            input_filter='float'
        )
        right_column.add_widget(self.entregar_input)

        # Botón entregar - REDUCIDO
        entregar_btn = ModernButton(
            text='ENTREGAR',
            bg_color=(0.85, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(35)  # Reducido de 40 a 35
        )
        entregar_btn.bind(on_press=self.entregar_dinero_manual)
        right_column.add_widget(entregar_btn)

        # Espaciador
        right_column.add_widget(Widget())

        columns_layout.add_widget(right_column)
        content_container.add_widget(columns_layout)

        # Botones principales (parte inferior)
        buttons_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )

        # Botón Ver Historial
        historial_btn = ModernButton(
            text='VER HISTORIAL',
            bg_color=(0.3, 0.6, 0.9, 1),
            size_hint_y=None,
            height=dp(45)
        )
        historial_btn.bind(on_press=self.ver_historial)
        buttons_container.add_widget(historial_btn)

        # Botón Regresar a Productos
        regresar_btn = ModernButton(
            text='REGRESAR',
            bg_color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(45)
        )
        regresar_btn.bind(on_press=self.regresar_productos)
        buttons_container.add_widget(regresar_btn)

        content_container.add_widget(buttons_container)

        # Feedback
        self.feedback_label = Label(
            text='',
            font_size=dp(12),
            color=(0.2, 0.6, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )
        content_container.add_widget(self.feedback_label)

        main_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))
        main_layout.add_widget(content_container)
        self.add_widget(main_layout)

    def regresar_productos(self, instance):
        """Regresar a la pantalla de productos"""
        self.manager.current = 'product_list'

    def agregar_dinero_manual(self, instance):
        """Agregar dinero manualmente a la caja"""
        try:
            cantidad_texto = self.dinero_input.text.strip()
            if not cantidad_texto:
                self.show_feedback('Ingresa una cantidad', error=True)
                return
            
            cantidad = float(cantidad_texto)
            if cantidad <= 0:
                self.show_feedback('La cantidad debe ser mayor a 0', error=True)
                return
            
            # Agregar al saldo
            self.saldo_actual += cantidad
            self.guardar_saldo(self.saldo_actual)
            self.actualizar_saldo_display()
            
            # Registrar en historial
            self.registrar_entrada_manual(cantidad)
            
            # Limpiar input
            self.dinero_input.text = ''
            
            # Mostrar confirmación
            self.show_feedback(f'${cantidad:.2f} agregado a la caja')
            
        except ValueError:
            self.show_feedback('Ingresa un número válido', error=True)

    def entregar_dinero_manual(self, instance):
        """Entregar dinero manualmente a la tesorera"""
        try:
            cantidad_texto = self.entregar_input.text.strip()
            if not cantidad_texto:
                self.show_feedback('Ingresa una cantidad a entregar', error=True)
                return
            
            cantidad = float(cantidad_texto)
            if cantidad <= 0:
                self.show_feedback('La cantidad debe ser mayor a 0', error=True)
                return
            
            if cantidad > self.saldo_actual:
                self.show_feedback('No puedes entregar más de lo que hay en caja', error=True)
                return
            
            # Popup de confirmación
            self.confirmar_entrega_manual(cantidad)
            
        except ValueError:
            self.show_feedback('Ingresa un número válido', error=True)

    def confirmar_entrega_manual(self, cantidad):
        """Mostrar popup de confirmación para entrega manual"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=[dp(15), dp(15)])
        
        # Información de la entrega
        info_label = Label(
            text=f'¿Entregar ${cantidad:.2f} a la tesorera?\n\nSaldo actual: ${self.saldo_actual:.2f}\nQuedará en caja: ${self.saldo_actual - cantidad:.2f}',
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(80),
            halign='center'
        )
        info_label.bind(texture_size=info_label.setter('text_size'))
        content.add_widget(info_label)

        # Botones
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        
        confirmar_btn = ModernButton(
            text='SÍ, ENTREGAR',
            bg_color=(0.2, 0.7, 0.3, 1)
        )
        cancelar_btn = ModernButton(
            text='CANCELAR',
            bg_color=(0.6, 0.6, 0.6, 1)
        )
        
        buttons_layout.add_widget(confirmar_btn)
        buttons_layout.add_widget(cancelar_btn)
        content.add_widget(buttons_layout)

        popup = Popup(
            title='Confirmar Entrega',
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False
        )

        def ejecutar_entrega(instance):
            self.ejecutar_entrega_manual(cantidad)
            popup.dismiss()

        confirmar_btn.bind(on_press=ejecutar_entrega)
        cancelar_btn.bind(on_press=popup.dismiss)
        popup.open()

    def ejecutar_entrega_manual(self, cantidad):
        """Ejecutar la entrega manual de dinero"""
        # Registrar en CSV usando cache optimizado
        fecha_actual = datetime.now()
        nuevo_saldo = self.saldo_actual - cantidad
        
        operation_data = {
            "fecha": fecha_actual.strftime('%Y-%m-%d'),
            "hora": fecha_actual.strftime('%H:%M:%S'),
            "tipo": "ENTREGA_MANUAL",
            "monto": f"{cantidad:.2f}",
            "saldo_anterior": f"{self.saldo_actual:.2f}",
            "saldo_nuevo": f"{nuevo_saldo:.2f}",
            "descripcion": "Entrega manual de dinero a tesorera"
        }
        cache.append_cash_history(operation_data)

        # Actualizar saldo
        self.saldo_actual = nuevo_saldo
        self.guardar_saldo(self.saldo_actual)
        self.actualizar_saldo_display()

        # Limpiar input
        self.entregar_input.text = ''

        # Mostrar confirmación
        if nuevo_saldo > 0:
            self.show_feedback(f'${cantidad:.2f} entregado a tesorera\nQueda en caja: ${nuevo_saldo:.2f}')
        else:
            self.show_feedback(f'${cantidad:.2f} entregado a tesorera\nCaja vacía')

    def registrar_entrada_manual(self, monto):
        """Registrar entrada manual en el historial CSV usando cache optimizado"""
        fecha_actual = datetime.now()
        
        operation_data = {
            "fecha": fecha_actual.strftime('%Y-%m-%d'),
            "hora": fecha_actual.strftime('%H:%M:%S'),
            "tipo": "ENTRADA",
            "monto": f"{monto:.2f}",
            "saldo_anterior": f"{self.saldo_actual - monto:.2f}",
            "saldo_nuevo": f"{self.saldo_actual:.2f}",
            "descripcion": "Entrada manual de dinero"
        }
        cache.append_cash_history(operation_data)

    def actualizar_saldo_display(self):
        """Actualizar la visualización del saldo"""
        self.saldo_label.text = f'${self.saldo_actual:.2f}'
        print(f"Saldo actualizado en pantalla: ${self.saldo_actual:.2f}")

    def agregar_venta(self, monto):
        """Agregar venta al saldo (llamado desde otras pantallas)"""
        self.saldo_actual += monto
        self.guardar_saldo(self.saldo_actual)
        self.actualizar_saldo_display()
        self.registrar_venta_en_historial(monto)
        print(f"Venta agregada: ${monto:.2f}, Nuevo saldo: ${self.saldo_actual:.2f}")

    def registrar_venta_en_historial(self, monto):
        """Registrar venta en el historial CSV usando cache optimizado"""
        fecha_actual = datetime.now()
        
        operation_data = {
            "fecha": fecha_actual.strftime('%Y-%m-%d'),
            "hora": fecha_actual.strftime('%H:%M:%S'),
            "tipo": "VENTA",
            "monto": f"{monto:.2f}",
            "saldo_anterior": f"{self.saldo_actual - monto:.2f}",
            "saldo_nuevo": f"{self.saldo_actual:.2f}",
            "descripcion": "Venta de productos"
        }
        cache.append_cash_history(operation_data)

    def ver_historial(self, instance):
        """Ver historial de cortes y ventas"""
        if not os.path.exists('historial_caja.csv'):
            self.show_feedback('No hay historial aún')
            return

        # Leer historial
        historial = []
        try:
            with open('historial_caja.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Saltar header
                for row in reader:
                    historial.append(row)
        except Exception as e:
            self.show_feedback(f'Error al leer historial: {str(e)}', error=True)
            return

        # Crear popup con historial más compacto
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(15), dp(15)])
        
        title = Label(
            text='HISTORIAL DE CAJA',
            font_size=dp(16),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(title)

        # ScrollView para el historial
        scroll = ScrollView()
        historial_layout = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
        historial_layout.bind(minimum_height=historial_layout.setter('height'))

        # Mostrar últimos 15 registros
        for registro in reversed(historial[-15:]):
            if len(registro) >= 4:
                fecha, tipo, monto, saldo_nuevo = registro
                fecha_corta = fecha.split(' ')[0]  # Solo la fecha
             
                # Color y prefijo según tipo
                if tipo == 'CORTE' or tipo == 'ENTREGA_MANUAL':
                    color = (0.8, 0.2, 0.2, 1)
                    prefijo = '[SALIDA]'
                elif tipo == 'ENTRADA':
                    color = (0.2, 0.2, 0.8, 1)
                    prefijo = '[INGRESO]'
                else:  # VENTA
                    color = (0.2, 0.6, 0.2, 1)
                    prefijo = '[VENTA]'
                
                # Texto según tipo
                if tipo == 'ENTREGA_MANUAL':
                    tipo_texto = 'ENTREGA'
                else:
                    tipo_texto = tipo
                
                item = Label(
                    text=f'{prefijo} {fecha_corta} | {tipo_texto} | ${monto}',
                    font_size=dp(11),
                    color=color,
                    size_hint_y=None,
                    height=dp(25),
                    halign='left'
                )
                item.bind(texture_size=item.setter('text_size'))
                historial_layout.add_widget(item)

        if not historial:
            no_data = Label(
                text='No hay registros en el historial',
                font_size=dp(13),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(40)
            )
            historial_layout.add_widget(no_data)

        scroll.add_widget(historial_layout)
        content.add_widget(scroll)

        # Botón cerrar
        cerrar_btn = ModernButton(
            text='CERRAR',
            bg_color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(35)
        )
        content.add_widget(cerrar_btn)

        popup = Popup(
            title='Historial',
            content=content,
            size_hint=(0.75, 0.6),
            auto_dismiss=False
        )
        
        cerrar_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_feedback(self, message, error=False):
        """Mostrar mensaje de feedback"""
        self.feedback_label.text = message
        self.feedback_label.color = (0.85, 0.2, 0.2, 1) if error else (0.2, 0.6, 0.2, 1)
        Clock.schedule_once(lambda dt: setattr(self.feedback_label, 'text', ''), 4)

    def on_enter(self):
        """Actualizar saldo al entrar a la pantalla"""
        print("Entrando a CajaScreen...")
        self.saldo_actual = self.cargar_saldo()
        self.actualizar_saldo_display()
        print(f"Saldo mostrado: {self.saldo_label.text}")