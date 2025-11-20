from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Rectangle
        from kivy.uix.widget import Widget
        from kivy.metrics import dp
        root = BoxLayout(orientation='vertical')
        with self.canvas.before:
            Color(0.2, 0.4, 0.6, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        scroll = ScrollView(size_hint=(1, 0.9))
        content_anchor = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(1, None))
        content = BoxLayout(orientation='vertical', padding=[20, 40, 20, 40], spacing=25, size_hint=(None, None), width=dp(380))
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Label(text="[b]Créditos[/b]", font_size=32, markup=True, size_hint_y=None, height=48, color=(1,1,1,1), halign='center', valign='middle', text_size=(dp(340), None), padding=(0, 18)))
        content.add_widget(Widget(size_hint_y=None, height=9))
        content.add_widget(Label(
            text="Esta aplicación y su código fuente son propiedad intelectual de Gloriela Suárez Castañeda. Su uso está limitado a usuarios autorizados. Queda prohibida la reproducción, distribución, modificación o cualquier uso no autorizado, total o parcial, sin el consentimiento expreso y por escrito de la autora.",
            font_size=18, color=(1,1,1,1), halign='center', valign='middle', size_hint_y=None, height=100, text_size=(dp(340), None), padding=(0, 18)
        ))
        content.add_widget(Widget(size_hint_y=None, height=9))
        content.add_widget(Label(
            text="El software se proporciona 'tal cual', sin garantías de ningún tipo. La autora no será responsable por daños derivados del uso o imposibilidad de uso.",
            font_size=16, color=(1,1,1,1), halign='center', valign='middle', size_hint_y=None, height=60, text_size=(dp(340), None), padding=(0, 18)
        ))
        content.add_widget(Widget(size_hint_y=None, height=9))
        content.add_widget(Label(
            text="Contacto: glo.suacas@gmail.com\n© 2025 Gloriela Suárez Castañeda. Todos los derechos reservados.",
            font_size=15, color=(1,1,1,1), halign='center', valign='middle', size_hint_y=None, height=50, text_size=(dp(340), None), padding=(0, 18)
        ))
        content_anchor.add_widget(content)
        scroll.add_widget(content_anchor)
        root.add_widget(scroll)
        btn_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 0.1), padding=[0, 0, 0, 24])
        btn_volver = Button(text="Empezar a vender", size_hint=(None, None), size=(200, 54), font_size=20, background_color=(0.2, 0.7, 0.2, 1), color=(1,1,1,1))  # Texto y ancho cambiados
        btn_volver.bind(on_release=self.volver_menu)
        btn_anchor.add_widget(btn_volver)
        root.add_widget(btn_anchor)
        self.add_widget(root)

    def _update_bg(self, *a):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def volver_menu(self, instance):
        # Limpiar todos los formularios y datos antes de ir a la lista de productos
        from kivy.app import App
        app = App.get_running_app()
        # Usar función centralizada de limpieza
        app.reset_all_data()
        self.manager.current = 'product_list'  # Ir directamente a la lista de productos