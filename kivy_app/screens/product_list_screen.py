from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from screens.optimized_image import OptimizedImage
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from screens.topbar import TopBar
from screens.data_cache import cache
import json

# Botón de imagen para números
class ImageButton(ButtonBehavior, Image):
    pass

# Tarjeta que se comporta como botón y se puede seleccionar
class Card(ButtonBehavior, BoxLayout):
    def __init__(self, prod, product_index, on_select, quantity=0, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(4), padding=dp(6), **kwargs)
        self.size_hint = (None, None)
        self.width = dp(110)
        self.height = dp(140)  # Reducimos más la altura ya que no hay botones
        self.on_select = on_select
        self.prod = prod
        self.product_index = product_index
        self.quantity = quantity

        # Fondo y borde
        with self.canvas.before:
            self.bg_color_instruction = Color(rgba=(1, 1, 1, 1))  # Fondo blanco inicial
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        # Actualizar la posición y tamaño del fondo
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Imagen del producto (simplificada para evitar problemas)
        img = Image(
            source=prod.get('image', 'assets/default_photo.png'),
            size_hint_y=None,
            height=dp(50),
            allow_stretch=True,
            keep_ratio=True
        )

        # Nombre del producto
        lbl_name = Label(
            text=prod.get('name', ''),
            font_size=dp(11),
            color=(0, 0, 0, 1),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(22)
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        # Precio
        lbl_price = Label(
            text=f"${prod.get('price', '')}",
            font_size=dp(10),
            color=(0, 0, 0, 1),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(18)
        )
        lbl_price.bind(size=lbl_price.setter('text_size'))

        # Agregar widgets a la tarjeta
        self.add_widget(img)
        self.add_widget(lbl_name)
        self.add_widget(lbl_price)

        # Aplicar estilo inicial según selección
        self.update_selection_style()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_selection_style(self):
        if self.quantity > 0:
            # Fondo verde semitransparente
            self.bg_color_instruction.rgba = (0.2, 0.7, 0.2, 0.5)
        else:
            self.bg_color_instruction.rgba = (1, 1, 1, 1)

    def on_press(self):
        self.on_select()


class ProductListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = {}  # {producto_index: cantidad}
        self.products = []
        self.selected_product_index = None
        self._interface_built = False  # Flag para evitar reconstrucciones
        
        # Layout principal con TopBar - construir una sola vez
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(TopBar(show_back=True))
        
        self.layout = BoxLayout(orientation='vertical', spacing=16, padding=16, size_hint_y=0.88)
        self.main_layout.add_widget(self.layout)
        self.add_widget(self.main_layout)
        
        # Cargar productos inicial
        self.load_products()

    def on_enter(self):
        """Recarga los productos solo si han cambiado"""
        current_products = cache.get_products()
        if current_products != self.products:
            print("🔄 Productos han cambiado, recargando interfaz...")
            self.products = current_products
            self.build_interface()
        else:
            print("⚡ Productos no han cambiado, manteniendo interfaz")

    def load_products(self):
        """Carga inicial de productos optimizada"""
        # Usar cache optimizado en lugar de leer archivo directamente
        self.products = cache.get_products()
        self.build_interface()
    
    def build_interface(self):
        """Construir la interfaz de usuario (separado de carga de datos) - OPTIMIZADO"""
        # Solo reconstruir si no está construida o productos han cambiado significativamente
        if self._interface_built and len(self.products) == getattr(self, '_last_product_count', 0):
            # Solo actualizar datos sin reconstruir UI
            self.update_cart_display()
            self.update_total()
            return
        
        print("🔨 Construyendo interfaz completa...")
        self.layout.clear_widgets()
        
        # Limpiar cache de tarjetas cuando se reconstruye
        if hasattr(self, '_product_cards'):
            del self._product_cards
        
        self._last_product_count = len(self.products)

        # Layout principal con productos y panel de cantidad
        main_content = BoxLayout(orientation='horizontal', spacing=10)
        
        # Panel izquierdo: Grid de productos
        products_panel = BoxLayout(orientation='vertical')
        
        # Título para productos
        products_title = Label(
            text='Selecciona productos:',
            font_size=18,
            size_hint_y=None,
            height=30,
            color=(0, 0, 0, 1)
        )
        products_panel.add_widget(products_title)

        # Cuadrícula de tarjetas de productos
        cols = 3
        products_scroll = ScrollView()
        grid_box = GridLayout(cols=cols, spacing=dp(12), padding=[dp(18), dp(18), dp(18), dp(10)], size_hint_y=None)
        grid_box.bind(minimum_height=grid_box.setter('height'))

        for idx, prod in enumerate(self.products):
            quantity = self.cart.get(idx, 0)
            card = Card(
                prod,
                idx,  # Pasar índice del producto
                on_select=lambda i=idx: self.select_product(i),
                quantity=quantity
            )
            grid_box.add_widget(card)

        products_scroll.add_widget(grid_box)
        products_panel.add_widget(products_scroll)
        
        # Panel derecho: Cantidad y carrito
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=10)
        
        # Título del panel de cantidad
        quantity_title = Label(
            text='Cantidad:',
            font_size=18,
            size_hint_y=None,
            height=30,
            color=(0, 0, 0, 1)
        )
        right_panel.add_widget(quantity_title)
        
        # Label para mostrar producto seleccionado
        self.selected_product_label = Label(
            text="Selecciona un producto",
            font_size=16,
            size_hint_y=None,
            height=40,
            color=(0, 0, 0, 1)
        )
        right_panel.add_widget(self.selected_product_label)
        
        # Grid de botones numéricos (2 filas de 5)
        numbers_grid = GridLayout(cols=5, rows=2, spacing=5, size_hint_y=None, height=160)
        for i in range(1, 11):
            btn = ImageButton(source=f"assets/{i}_copies.png", size_hint=(1, 1))
            btn.bind(on_release=lambda inst, n=i: self.add_quantity(n))
            numbers_grid.add_widget(btn)
        right_panel.add_widget(numbers_grid)
        
        # Carrito de compra
        cart_title = Label(
            text='Carrito:',
            font_size=18,
            size_hint_y=None,
            height=30,
            color=(0, 0, 0, 1)
        )
        right_panel.add_widget(cart_title)
        
        # ScrollView para el carrito
        cart_scroll = ScrollView(size_hint_y=0.4)
        self.cart_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        cart_scroll.add_widget(self.cart_layout)
        right_panel.add_widget(cart_scroll)
        
        # Total
        self.total_label = Label(
            text='Total: $0.00',
            font_size=20,
            size_hint_y=None,
            height=40,
            color=(0, 0, 0, 1),
            bold=True
        )
        right_panel.add_widget(self.total_label)
        
        main_content.add_widget(products_panel)
        main_content.add_widget(right_panel)
        self.layout.add_widget(main_content)
        
        # Botones inferiores: Corregir, Modificar Lista, CAJA y Continuar
        bottom_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(10), 0])

        # Botón corregir (limpiar carrito)
        btn_corregir = Button(
            text='Corregir',
            background_color=(0.7, 0.5, 0.2, 1),
            size_hint_x=0.25
        )
        btn_corregir.bind(on_release=self.go_correccion)

        # Botón modificar lista
        btn_modificar = Button(
            text='Modificar Lista',
            background_color=(0.2, 0.5, 0.7, 1),
            size_hint_x=0.25,
            font_size=dp(12)
        )
        btn_modificar.bind(on_release=self.go_add_product)

        # BOTÓN CAJA - AGREGADO
        btn_caja = Button(
            text='CAJA',
            background_color=(0.9, 0.6, 0.2, 1),  # Color dorado
            size_hint_x=0.25,
            font_size=dp(14)
        )
        btn_caja.bind(on_release=self.ir_a_caja)

        # Botón continuar (solo visible si hay productos en carrito)
        self.continue_btn = Button(
            text='Continuar', 
            size_hint_x=0.25,
            background_color=(0.2, 0.7, 0.2, 1)  # Verde
        )
        self.continue_btn.bind(on_release=self.go_to_confirm)
        self.update_continue_btn()
        
        bottom_buttons.add_widget(btn_corregir)
        bottom_buttons.add_widget(btn_modificar)
        bottom_buttons.add_widget(btn_caja)
        bottom_buttons.add_widget(self.continue_btn)
        
        self.layout.add_widget(bottom_buttons)
        
        # Marcar interfaz como construida
        self._interface_built = True
        
        # Actualizar interfaz solo una vez al final
        self.update_cart_display()
        self.update_total()
        
        print("✅ Interfaz construida completamente")

    def select_product(self, idx):
        self.selected_product_index = idx
        if idx < len(self.products):
            product_name = self.products[idx]['name']
            current_qty = self.cart.get(idx, 0)
            self.selected_product_label.text = f"{product_name}\nCantidad actual: {current_qty}"

    def add_quantity(self, quantity):
        if self.selected_product_index is not None:
            self.cart[self.selected_product_index] = self.cart.get(self.selected_product_index, 0) + quantity
            self.update_cart_display()
            self.update_total()
            self.update_products_display()
            self.update_continue_btn()
            # Actualizar label del producto seleccionado
            current_qty = self.cart.get(self.selected_product_index, 0)
            product_name = self.products[self.selected_product_index]['name']
            self.selected_product_label.text = f"{product_name}\nCantidad actual: {current_qty}"

    def update_products_display(self):
        """Actualizar el estilo visual de las tarjetas de productos - OPTIMIZADO"""
        # Mantener referencia a las tarjetas para evitar búsqueda repetitiva
        if not hasattr(self, '_product_cards'):
            self._product_cards = []
            # Encontrar y cachear las tarjetas una sola vez
            for child in self.layout.children:
                if isinstance(child, BoxLayout):  # main_content
                    for panel in child.children:
                        if isinstance(panel, BoxLayout):  # products_panel
                            for widget in panel.children:
                                if isinstance(widget, ScrollView):  # products_scroll
                                    for grid in widget.children:
                                        if isinstance(grid, GridLayout):
                                            for card in grid.children:
                                                if isinstance(card, Card):
                                                    self._product_cards.append(card)
        
        # Actualizar solo las tarjetas que necesitan cambio
        for card in self._product_cards:
            if hasattr(card, 'product_index') and card.product_index is not None:
                new_quantity = self.cart.get(card.product_index, 0)
                if card.quantity != new_quantity:
                    card.quantity = new_quantity
                    card.update_selection_style()

    def update_cart_display(self):
        self.cart_layout.clear_widgets()
        for product_idx, quantity in self.cart.items():
            if quantity > 0 and product_idx < len(self.products):
                product = self.products[product_idx]
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)
                
                # Información del producto
                info_text = f"{product['name']} x{quantity} = ${float(product['price']) * quantity:.2f}"
                info_label = Label(
                    text=info_text,
                    font_size=12,
                    color=(0, 0, 0, 1),
                    text_size=(None, None),
                    halign='left'
                )
                
                # Botón para eliminar
                remove_btn = Button(
                    text='X',
                    size_hint=(None, None),
                    size=(30, 30),
                    background_color=(0.8, 0.2, 0.2, 1)
                )
                remove_btn.bind(on_release=lambda inst, idx=product_idx: self.remove_from_cart(idx))
                
                item_layout.add_widget(info_label)
                item_layout.add_widget(remove_btn)
                self.cart_layout.add_widget(item_layout)

    def remove_from_cart(self, product_idx):
        if product_idx in self.cart:
            del self.cart[product_idx]
            self.update_cart_display()
            self.update_total()
            self.update_products_display()
            self.update_continue_btn()

    def update_total(self):
        total = 0
        for product_idx, quantity in self.cart.items():
            if product_idx < len(self.products):
                price = float(self.products[product_idx]['price'])
                total += price * quantity
        self.total_label.text = f'Total: ${total:.2f}'

    def update_continue_btn(self):
        has_items = any(qty > 0 for qty in self.cart.values())
        if has_items:
            self.continue_btn.opacity = 1
            self.continue_btn.disabled = False
        else:
            self.continue_btn.opacity = 0.5
            self.continue_btn.disabled = True

    def go_to_confirm(self, instance):
        # Guardar carrito en la app para usar en confirm_screen
        from kivy.app import App
        app = App.get_running_app()
        app.shopping_cart = self.cart.copy()
        app.products_list = self.products.copy()
        self.manager.current = 'confirm'

    def go_correccion(self, instance):
        """Función de corrección - Limpiar el carrito para volver a seleccionar productos"""
        # Limpiar el carrito
        self.cart = {}
        self.selected_product_index = None
        
        # Actualizar la interfaz
        if hasattr(self, 'selected_product_label'):
            self.selected_product_label.text = "Selecciona un producto"
        if hasattr(self, 'total_label'):
            self.total_label.text = 'Total: $0.00'
        if hasattr(self, 'cart_layout'):
            self.cart_layout.clear_widgets()
        
        # Actualizar botones y visualización
        self.update_continue_btn()
        self.update_products_display()
        
        # Mostrar mensaje de confirmación
        popup = Popup(
            title='Carrito Limpiado',
            content=Label(text='El carrito ha sido limpiado.\nPuedes volver a seleccionar productos.'),
            size_hint=(None, None),
            size=(350, 200)
        )
        popup.open()
        
        # Cerrar popup automáticamente después de 2 segundos
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def edit_product(self, product_index):
        """Editar producto existente"""
        if 0 <= product_index < len(self.products):
            product_data = self.products[product_index]
            manager_screen = self.manager.get_screen('product_manager')
            manager_screen.setup_for_editing(product_index, product_data)
            self.manager.current = 'product_manager'

    def go_add_product(self, instance):
        """Ir a la pantalla de gestión de productos"""
        self.manager.current = 'product_manager'

    def ir_a_caja(self, instance):
        """Ir a la pantalla de caja"""
        self.manager.current = 'caja'