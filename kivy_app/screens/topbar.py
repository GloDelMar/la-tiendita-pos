from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class TopBar(BoxLayout):
    def __init__(self, show_back=False, back_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.back_screen = back_screen  # Pantalla de destino personalizada
        self.orientation = "horizontal"
        self.size_hint_y = 0.15  # Aumentado de 0.12 a 0.15
        self.padding = [10, 15]  # Aumentado padding vertical
        self.spacing = 10

        with self.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        from kivy.uix.anchorlayout import AnchorLayout
        center_box = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 1))
        logo = Image(source="assets/cam15_logo.png", size_hint=(None, None), size=(48, 48))
        title = Label(
            text="Contabilidad",
            color=(1, 1, 1, 1),
            font_size="25sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint=(None, 1),
            size=(220, 1)
        )
        title.bind(texture_size=title.setter("size"))
        center_box.add_widget(logo)
        center_box.add_widget(title)
        center_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
        center_anchor.add_widget(center_box)

        from kivy.uix.behaviors import ButtonBehavior
        class ImageButton(ButtonBehavior, Image):
            pass

        # --- Botones del TopBar ---
        credits_img_path = 'assets/idea.png'
        btn_credits = ImageButton(
            source=credits_img_path,
            size_hint=(None, None),
            size=(48, 48),  # Aumentado de 36x36 a 48x48
        )
        btn_credits.bind(on_release=self.go_credits)

        # Botón de Recibos (Historial)
        btn_recibos = ImageButton(
            source='assets/tablon_recibos.png',
            size_hint=(None, None),
            size=(48, 48),  # Aumentado de 36x36 a 48x48
        )
        btn_recibos.bind(on_release=self.go_historial)

        # Botón de Transacciones
        btn_transacciones = ImageButton(
            source='assets/tablon_transacciones.png',
            size_hint=(None, None),
            size=(48, 48),  # Aumentado de 36x36 a 48x48
        )
        btn_transacciones.bind(on_release=self.go_transacciones)

        self.add_widget(center_anchor)
        if show_back:
            btn_volver = ImageButton(
                source='assets/volver.png',
                size_hint=(None, None),
                size=(48, 48),  # Aumentado de 36x36 a 48x48
            )
            btn_volver.bind(on_release=self.volver_pantalla)
            right_box = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=250, spacing=6)  # Aumentado width y spacing para botones más grandes
            right_box.add_widget(btn_recibos)
            right_box.add_widget(btn_transacciones)
            right_box.add_widget(btn_credits)
            right_box.add_widget(btn_volver)
            right_anchor = AnchorLayout(anchor_x='right', anchor_y='center', size_hint=(None, 1), width=250)
            right_anchor.add_widget(right_box)
            self.add_widget(right_anchor)
        else:
            right_box = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=200, spacing=6)  # Aumentado width y spacing para botones más grandes
            right_box.add_widget(btn_recibos)
            right_box.add_widget(btn_transacciones)
            right_box.add_widget(btn_credits)
            right_anchor = AnchorLayout(anchor_x='right', anchor_y='center', size_hint=(None, 1), width=200)
            right_anchor.add_widget(right_box)
            self.add_widget(right_anchor)

    def go_credits(self, instance):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'root'):
            app.root.current = 'credits'

    def go_historial(self, instance):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'root'):
            app.root.current = 'historial'

    def go_transacciones(self, instance):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'root'):
            app.root.current = 'transacciones'

    def volver_pantalla(self, instance):
        from kivy.app import App
        app = App.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'current'):
            # Limpiar formulario si estamos en add_product_screen
            current_screen = app.root.current
            if current_screen == 'add_product':
                try:
                    add_product_screen = app.root.get_screen('add_product')
                    if hasattr(add_product_screen, 'clear_form'):
                        add_product_screen.clear_form()
                except Exception:
                    pass  # Ignorar errores si la pantalla no existe
            
            # Si hay una pantalla de destino específica, ir a esa pantalla
            if self.back_screen:
                app.root.current = self.back_screen
            else:
                # Comportamiento por defecto: ir a la lista de productos
                if app.root.current != 'product_list':
                    # Limpiar todos los datos antes de regresar a productos
                    if hasattr(app, 'reset_all_data'):
                        app.reset_all_data()
                    app.root.current = 'product_list'  # Cambiado de 'main_menu' a 'product_list'

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos