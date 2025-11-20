
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
# Botón imagen reutilizable
class ImageButton(ButtonBehavior, Image):
    pass
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle, Line

class MonedasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.seleccion = []

        # Root vertical: 3 filas
        root = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # --- Barra superior con botón regresar y corregir ---
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout
        # Contenedor barra superior
        topbar = KivyBoxLayout(orientation='horizontal', size_hint_y=None, height=54, spacing=0, padding=[0,0,0,0])
        # Contenedor para botón regresar
        back_container = AnchorLayout(anchor_x='left', anchor_y='center', size_hint_x=None, width=60)
        btn_back = ImageButton(source='assets/volver.png', size_hint=(None, None), size=(44, 44), allow_stretch=True)
        btn_back.bind(on_release=self.go_back)
        back_container.add_widget(btn_back)
        # Contenedor para botón corregir
        clear_container = AnchorLayout(anchor_x='left', anchor_y='center', size_hint_x=None, width=120)
        btn_clear = Button(text='Corregir', size_hint=(None, None), size=(100, 44), background_color=(0.8,0.3,0.3,1), font_size=16)
        btn_clear.bind(on_release=self.clear_seleccion)
        clear_container.add_widget(btn_clear)
        # Espaciador para alinear a la izquierda
        topbar.add_widget(back_container)
        topbar.add_widget(clear_container)
        topbar.add_widget(Label(size_hint_x=1, text=''))
        root.add_widget(topbar)


        # --- Fila superior: monedas y billetes centrados, total debajo ---
        from kivy.uix.anchorlayout import AnchorLayout
        monedas_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, None))
        img_map = {
            0.5: 'm_050.png',
            1: 'm_1.png',
            2: 'm_2.png',
            5: 'm_5.png',
            10: 'b_10.png',
            20: 'b_20.png',
            50: 'b_50.png',
            100: 'b_100.png',
            200: 'b_200.png',
        }
        monedas = [0.5, 1, 2, 5]
        billetes = [10, 20, 50, 100, 200]

        row_monedas = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), height=100)
        for m in monedas:
            img_path = f"assets/{img_map[m]}"
            btn = ImageButton(source=img_path, allow_stretch=True, keep_ratio=True, size_hint=(None, None), size=(90, 90))
            btn.monto = m
            btn.bind(on_release=self.on_monto_click)
            row_monedas.add_widget(btn)
        row_monedas.width = (90+10)*len(monedas) - 10
        anchor_monedas = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=100)
        anchor_monedas.add_widget(row_monedas)

        row_billetes = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), height=90)
        for b in billetes:
            img_path = f"assets/{img_map[b]}"
            btn = ImageButton(source=img_path, allow_stretch=True, keep_ratio=True, size_hint=(None, None), size=(120, 70))
            btn.monto = b
            btn.bind(on_release=self.on_monto_click)
            row_billetes.add_widget(btn)
        row_billetes.width = (120+10)*len(billetes) - 10
        anchor_billetes = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height=90)
        anchor_billetes.add_widget(row_billetes)

        monedas_box.add_widget(anchor_monedas)
        monedas_box.add_widget(anchor_billetes)
        monedas_box.height = 100 + 90 + 10

        # Total debajo, centrado
        total_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=40)
        self.resumen_label = Label(text='Total: $0.00', font_size=22, color=(0.1,0.2,0.4,1))
        total_box.add_widget(self.resumen_label)

        # Contenedor vertical para la parte superior
        top_box = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=5)
        top_box.add_widget(monedas_box)
        top_box.add_widget(total_box)

        # --- Fila 2: 60% alto (acumulación monedas clickeadas) ---
        middle_box = BoxLayout(orientation='vertical', size_hint_y=0.4)
        # Borde simulando caja
        with middle_box.canvas.before:
            Color(0.8,0.8,0.8,1)
            self.bg_rect = Rectangle(pos=middle_box.pos, size=middle_box.size)
            Color(0,0,0,1)
            self.border_line = Line(rectangle=(middle_box.x, middle_box.y, middle_box.width, middle_box.height), width=2)
        middle_box.bind(pos=self.update_border, size=self.update_border)

        scroll_seleccion = ScrollView()
        self.seleccion_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=80, padding=[5,5,5,5])
        scroll_seleccion.add_widget(self.seleccion_box)
        middle_box.add_widget(scroll_seleccion)

        # --- Fila 3: 10% alto (botón listo) ---
        bottom_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=0.1)
        btn_listo = Button(text='Listo', size_hint=(None,None), height=50, background_color=(0.4,0.7,1,1), padding=(20,10))
        btn_listo.bind(on_release=self.set_pago_and_return)
        bottom_box.add_widget(btn_listo)

        # --- Agregar filas al root ---
        root.add_widget(top_box)
        root.add_widget(middle_box)
        root.add_widget(bottom_box)
        self.add_widget(root)

    def go_back(self, inst):
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = 'confirm'

    def clear_seleccion(self, inst):
        self.seleccion = []
        self.update_seleccion()

    def clear_all_data(self):
        """Limpia todos los datos de selección de monedas"""
        self.seleccion = []
        self.update_seleccion()

    def on_monto_click(self, btn):
        self.seleccion.append(btn.monto)
        self.update_seleccion()

    def update_seleccion(self):
        self.seleccion_box.clear_widgets()
        if self.seleccion:
            conteo = {}
            for v in self.seleccion:
                conteo[v] = conteo.get(v,0)+1
            img_map = {0.5:'m_050.png',1:'m_1.png',2:'m_2.png',5:'m_5.png',
                       10:'b_10.png',20:'b_20.png',50:'b_50.png',100:'b_100.png',200:'b_200.png'}
            for k in sorted(conteo):
                img_path = f"assets/{img_map[k]}" if k in img_map else ''
                for _ in range(conteo[k]):
                    img_widget = Image(source=img_path, size_hint=(None,None), size=(48,48))
                    self.seleccion_box.add_widget(img_widget)
            total = sum(self.seleccion)
            self.resumen_label.text = f'Total: ${total:.2f}'
        else:
            self.resumen_label.text = 'Total: $0.00'

    def update_border(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def set_pago_and_return(self, inst):
        total = sum(self.seleccion)
        from kivy.app import App
        app = App.get_running_app()
        confirm_screen = app.root.get_screen('confirm')
        pago_str = f"{total:.2f}" if total else ''
        confirm_screen.pago_input.text = pago_str
        # También actualizar el pizarrón (operacion_label) usando el carrito
        cart_total = 0
        if hasattr(app, 'shopping_cart') and hasattr(app, 'products_list'):
            for product_idx, quantity in app.shopping_cart.items():
                if product_idx < len(app.products_list):
                    price = float(app.products_list[product_idx]['price'])
                    cart_total += price * quantity
        confirm_screen.operacion_label.text = f"{pago_str} - {cart_total:.2f} ="
        app.root.current = 'confirm'
