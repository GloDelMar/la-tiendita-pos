from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from screens.topbar import TopBar
import os, csv, json
import datetime

class TransaccionesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import datetime
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar(show_back=True))
        content = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20, 20, 20], size_hint_y=0.82)
        title = Label(text='Transacciones y Contabilidad', font_size=24, bold=True, color=(0.1,0.2,0.4,1), size_hint=(1, 0.1))
        content.add_widget(title)
        self.view_mode = 'dia'
        selector = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=5)
        # Azul accesible y amigable para daltónicos (azul-verdoso)
        btn_color = (0.13, 0.55, 0.80, 1)  # #2196B3
        btn_color_active = (0.09, 0.36, 0.55, 1)  # #175a8c
        class BlueButton(Button):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.background_normal = ''
                self.background_color = btn_color
                self.color = (1,1,1,1)
                self.font_size = 18
                self.size_hint = (1, 1)
                self.height = 40
                self.background_down = ''
                self.bind(pos=self._update_rect, size=self._update_rect)
                with self.canvas.before:
                    Color(*btn_color)
                    self._rounded_rect = RoundedRectangle(radius=[14], pos=self.pos, size=self.size)
            def _update_rect(self, *a):
                self._rounded_rect.pos = self.pos
                self._rounded_rect.size = self.size
        self.btn_dia = BlueButton(text='Día', on_press=lambda i: self.set_view('dia'))
        self.btn_semana = BlueButton(text='Semana', on_press=lambda i: self.set_view('semana'))
        self.btn_mes = BlueButton(text='Mes', on_press=lambda i: self.set_view('mes'))
        self.btn_anio = BlueButton(text='Año', on_press=lambda i: self.set_view('anio'))
        selector.add_widget(self.btn_dia)
        selector.add_widget(self.btn_semana)
        selector.add_widget(self.btn_mes)
        selector.add_widget(self.btn_anio)
        content.add_widget(selector)
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        content.add_widget(self.scroll)
        # Botones inferiores
        class RedButton(Button):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.background_normal = ''
                self.background_color = (0.85, 0.2, 0.2, 1)
                self.color = (1,1,1,1)
                self.font_size = 20
                self.size_hint = (None, None)
                self.height = 48
                self.padding = [24, 12]
                self.background_down = ''
                self.bind(texture_size=self._update_width)
                with self.canvas.before:
                    Color(0.85, 0.2, 0.2, 1)
                    self._rounded_rect = RoundedRectangle(radius=[16], pos=self.pos, size=self.size)
                self.bind(pos=self._update_rect, size=self._update_rect)
            def _update_width(self, *a):
                self.width = self.texture_size[0] + 48
            def _update_rect(self, *a):
                self._rounded_rect.pos = self.pos
                self._rounded_rect.size = self.size
        btn = RedButton(text='Volver', on_press=self.go_back)
        deudores_btn = Button(text='DEUDORES', size_hint=(None, None), height=48, width=160, background_color=(1, 0.6, 0, 1), color=(1,1,1,1), background_normal='', background_down='')
        deudores_btn.bind(on_press=self.go_deudores)
        bottom_row = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=[0,0,0,0])
        bottom_row.add_widget(deudores_btn)
        bottom_row.add_widget(Label(size_hint_x=1))
        bottom_row.add_widget(btn)
        content.add_widget(bottom_row)
        root.add_widget(content)
        self.add_widget(root)

    def go_deudores(self, instance):
        self.manager.current = 'deudores'

    def set_view(self, modo):
        self.view_mode = modo
        self.on_pre_enter()

    def on_pre_enter(self, *args):
        import datetime
        self.grid.clear_widgets()
        if not os.path.exists('transacciones.csv'):
            self.grid.add_widget(Label(text="No hay transacciones registradas.", font_size=16, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
            return
        with open('transacciones.csv', 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        if not reader:
            self.grid.add_widget(Label(text="No hay transacciones registradas.", font_size=16, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
            return
        def parse_fecha(s):
            try:
                return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            except:
                return None
        datos = [dict(row, _fecha=parse_fecha(row['fecha'])) for row in reader if parse_fecha(row['fecha'])]
        if self.view_mode == 'dia':
            dias = {}
            for row in datos:
                d = row['_fecha'].date()
                dias.setdefault(d, []).append(row)
            for d in sorted(dias.keys(), reverse=True):
                self.grid.add_widget(Label(text=str(d), font_size=18, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=32))
                header = BoxLayout(orientation='horizontal', size_hint_y=None, height=28)
                header_color = (0.10, 0.46, 0.82, 1)  # Azul accesible
                for h in ['nombre','grupo','precio','total','pago','cambio','pagado']:
                    label = h.capitalize() if h != 'precio' else 'Precio'
                    header.add_widget(Label(text=label, font_size=13, bold=True, color=header_color))
                self.grid.add_widget(header)
                total_dia = 0
                precio_color = (0.95, 0.55, 0.15, 1)  # naranja accesible
                for row in dias[d]:
                    row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=26)
                    for h in ['nombre','grupo','precio','total','pago','cambio','pagado']:
                        if h == 'precio':
                            row_box.add_widget(Label(text=str(row.get(h, '')), font_size=12, color=precio_color))
                        else:
                            row_box.add_widget(Label(text=str(row.get(h, '')), font_size=12, color=(0.1,0.2,0.4,1)))
                    try:
                        total_dia += float(row.get('total', 0))
                    except:
                        pass
                    self.grid.add_widget(row_box)
                # Suma de totales del día
                suma_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=24)
                suma_box.add_widget(Label(text=''))  # nombre
                suma_box.add_widget(Label(text=''))  # grupo
                suma_box.add_widget(Label(text=''))  # precio
                suma_box.add_widget(Label(text=f"${total_dia:.2f}", font_size=13, bold=True, color=(0.2,0.5,0.2,1)))  # total
                suma_box.add_widget(Label(text=''))  # pago
                suma_box.add_widget(Label(text=''))  # cambio
                suma_box.add_widget(Label(text=''))  # pagado
                self.grid.add_widget(suma_box)
        elif self.view_mode == 'semana':
            from collections import defaultdict
            semanas = defaultdict(lambda: defaultdict(list))
            for row in datos:
                dt = row['_fecha']
                year, week, _ = dt.isocalendar()
                semanas[(year, week)][dt.weekday()].append(row)
            dias_sem = ['Lunes','Martes','Miércoles','Jueves','Viernes']
            for (year, week) in sorted(semanas.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"Semana {week} - {year}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                header = BoxLayout(orientation='horizontal', size_hint_y=None, height=28)
                for d in dias_sem:
                    header.add_widget(Label(text=d, font_size=13, bold=True, color=(0.1,0.2,0.4,1)))
                header.add_widget(Label(text='Total semana', font_size=13, bold=True, color=(0.1,0.2,0.4,1)))
                self.grid.add_widget(header)
                row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=26)
                total_sem = 0
                for i in range(5):
                    day_rows = semanas[(year, week)].get(i, [])
                    total_dia = sum(float(r['total']) for r in day_rows)
                    row_box.add_widget(Label(text=f"${total_dia:.2f}", font_size=12, color=(0.1,0.2,0.4,1)))
                    total_sem += total_dia
                row_box.add_widget(Label(text=f"${total_sem:.2f}", font_size=12, bold=True, color=(0.1,0.2,0.4,1)))
                self.grid.add_widget(row_box)
        elif self.view_mode == 'mes':
            from collections import defaultdict
            meses = defaultdict(float)
            for row in datos:
                dt = row['_fecha']
                key = (dt.year, dt.month)
                meses[key] += float(row['total'])
            for (y, m) in sorted(meses.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"{y}-{m:02d}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                self.grid.add_widget(Label(text=f"Total: ${meses[(y,m)]:.2f}", font_size=15, color=(0.1,0.2,0.4,1), size_hint_y=None, height=24))
        elif self.view_mode == 'anio':
            from collections import defaultdict
            anios = defaultdict(float)
            for row in datos:
                dt = row['_fecha']
                anios[dt.year] += float(row['total'])
            suma = 0
            for y in sorted(anios.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"Año {y}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                self.grid.add_widget(Label(text=f"Total: ${anios[y]:.2f}", font_size=15, color=(0.1,0.2,0.4,1), size_hint_y=None, height=24))
                suma += anios[y]
            self.grid.add_widget(Label(text=f"Suma total: ${suma:.2f}", font_size=16, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=28))

    def go_back(self, instance):
        self.manager.current = 'product_list'
