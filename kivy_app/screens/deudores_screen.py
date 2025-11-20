from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from screens.topbar import TopBar
import os, json

class DeudoresScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar(show_back=True))
        content = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20, 20, 20])
        title = Label(text='Lista de Deudores', font_size=24, bold=True, color=(0.7,0.2,0.2,1), size_hint=(1, 0.1))
        content.add_widget(title)
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        content.add_widget(self.scroll)
        btn = Button(text='Volver', size_hint=(None, None), height=48, width=120, background_color=(0.85, 0.2, 0.2, 1), color=(1,1,1,1), background_normal='', background_down='')
        btn.bind(on_press=self.go_back)
        content.add_widget(btn)
        root.add_widget(content)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.grid.clear_widgets()
        deudores = self.cargar_deudores()
        if not deudores:
            self.grid.add_widget(Label(text="No hay deudores", font_size=16, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
        else:
            for d in deudores:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
                row.add_widget(Label(text=d['nombre'], font_size=15, color=(0.7,0.2,0.2,1), size_hint_x=0.4))
                row.add_widget(Label(text=d['grupo'], font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.3))
                row.add_widget(Label(text=f"${d['deuda']:.2f}", font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.2))
                btn_pagado = Button(text="Pagado", size_hint=(None, 1), width=90, background_color=(0.2,0.7,0.2,1), color=(1,1,1,1), background_normal='', background_down='')
                btn_pagado.bind(on_press=lambda inst, nombre=d['nombre']: self.eliminar_deudor(nombre))
                row.add_widget(btn_pagado)
                self.grid.add_widget(row)
            total = sum(d['deuda'] for d in deudores)
            self.grid.add_widget(Label(text=f"Total deuda: ${total:.2f}", font_size=16, bold=True, color=(0.7,0.2,0.2,1), size_hint_y=None, height=30))

    def cargar_deudores(self):
        if not os.path.exists('deudores.json'):
            return []
        with open('deudores.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def guardar_deudores(self, deudores):
        with open('deudores.json', 'w', encoding='utf-8') as f:
            json.dump(deudores, f, ensure_ascii=False, indent=2)

    def eliminar_deudor(self, nombre):
        deudores = self.cargar_deudores()
        deudores = [d for d in deudores if d['nombre'] != nombre]
        self.guardar_deudores(deudores)
        self.on_pre_enter()

    def go_back(self, instance):
        self.manager.current = 'transacciones'
