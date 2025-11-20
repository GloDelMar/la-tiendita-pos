from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from screens.topbar import TopBar
import os

class HistorialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar(show_back=True))
        content = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20, 20, 20], size_hint_y=0.82)
        title = Label(text='Historial de Recibos', font_size=24, bold=True, color=(0.1,0.2,0.4,1), size_hint=(1, 0.1))
        content.add_widget(title)
        import datetime
        self.view_mode = 'dia'
        selector = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=5)
        btn_color = (0.13, 0.55, 0.80, 1)  # #2196B3 accesible
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
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
        self.scroll = ScrollView(size_hint=(1, 0.72))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        content.add_widget(self.scroll)
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
        from kivy.uix.anchorlayout import AnchorLayout
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
        btn_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=0.1)
        btn_anchor.add_widget(btn)
        content.add_widget(btn_anchor)
        root.add_widget(content)
        self.add_widget(root)

    def set_view(self, modo):
        self.view_mode = modo
        self.on_pre_enter()

    def on_pre_enter(self, *args):
        import datetime
        self.grid.clear_widgets()
        pdf_files = [f for f in os.listdir('.') if f.startswith('recibo_') and f.endswith('.pdf')]
        if not pdf_files:
            self.grid.add_widget(Label(text="No hay recibos PDF generados.", font_size=16, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
            return
        # Parse fechas de los archivos
        def parse_fecha_from_filename(f):
            try:
                return datetime.datetime.strptime(f[7:26], '%Y-%m-%d_%H-%M-%S')
            except:
                return None
        archivos = [dict(nombre=f, fecha=parse_fecha_from_filename(f)) for f in pdf_files if parse_fecha_from_filename(f)]
        orange_color = (1, 0.6, 0, 1)
        if self.view_mode == 'dia':
            dias = {}
            for row in archivos:
                d = row['fecha'].date()
                dias.setdefault(d, []).append(row)
            for d in sorted(dias.keys(), reverse=True):
                self.grid.add_widget(Label(text=str(d), font_size=18, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=32))
                for row in dias[d]:
                    row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
                    row_box.add_widget(Label(text=row['nombre'], font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.7, valign='middle', halign='left'))
                    btn = Button(text='Ver', size_hint=(None, 1), font_size=15, color=(1,1,1,1), background_normal='', background_color=orange_color, padding=[18, 8])
                    btn.bind(on_press=lambda inst, path=row['nombre']: self.descargar_pdf(path))
                    btn.bind(texture_size=lambda inst, *a: setattr(inst, 'width', inst.texture_size[0] + 36))
                    row_box.add_widget(btn)
                    self.grid.add_widget(row_box)
        elif self.view_mode == 'semana':
            from collections import defaultdict
            semanas = defaultdict(list)
            for row in archivos:
                dt = row['fecha']
                year, week, _ = dt.isocalendar()
                semanas[(year, week)].append(row)
            for (year, week) in sorted(semanas.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"Semana {week} - {year}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                for row in semanas[(year, week)]:
                    row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
                    row_box.add_widget(Label(text=row['nombre'], font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.7, valign='middle', halign='left'))
                    btn = Button(text='Ver', size_hint=(None, 1), font_size=15, color=(1,1,1,1), background_normal='', background_color=orange_color, padding=[18, 8])
                    btn.bind(on_press=lambda inst, path=row['nombre']: self.descargar_pdf(path))
                    btn.bind(texture_size=lambda inst, *a: setattr(inst, 'width', inst.texture_size[0] + 36))
                    row_box.add_widget(btn)
                    self.grid.add_widget(row_box)
        elif self.view_mode == 'mes':
            from collections import defaultdict
            meses = defaultdict(list)
            for row in archivos:
                dt = row['fecha']
                meses[(dt.year, dt.month)].append(row)
            for (year, month) in sorted(meses.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"{year}-{month:02d}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                for row in meses[(year, month)]:
                    row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
                    row_box.add_widget(Label(text=row['nombre'], font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.7, valign='middle', halign='left'))
                    btn = Button(text='Ver', size_hint=(None, 1), font_size=15, color=(1,1,1,1), background_normal='', background_color=orange_color, padding=[18, 8])
                    btn.bind(on_press=lambda inst, path=row['nombre']: self.descargar_pdf(path))
                    btn.bind(texture_size=lambda inst, *a: setattr(inst, 'width', inst.texture_size[0] + 36))
                    row_box.add_widget(btn)
                    self.grid.add_widget(row_box)
        elif self.view_mode == 'anio':
            from collections import defaultdict
            anios = defaultdict(list)
            for row in archivos:
                dt = row['fecha']
                anios[dt.year].append(row)
            for year in sorted(anios.keys(), reverse=True):
                self.grid.add_widget(Label(text=f"Año {year}", font_size=17, bold=True, color=(0.1,0.2,0.4,1), size_hint_y=None, height=30))
                for row in anios[year]:
                    row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
                    row_box.add_widget(Label(text=row['nombre'], font_size=15, color=(0.1,0.2,0.4,1), size_hint_x=0.7, valign='middle', halign='left'))
                    btn = Button(text='Ver', size_hint=(None, 1), font_size=15, color=(1,1,1,1), background_normal='', background_color=orange_color, padding=[18, 8])
                    btn.bind(on_press=lambda inst, path=row['nombre']: self.descargar_pdf(path))
                    btn.bind(texture_size=lambda inst, *a: setattr(inst, 'width', inst.texture_size[0] + 36))
                    row_box.add_widget(btn)
                    self.grid.add_widget(row_box)

    def descargar_pdf(self, pdf_path):
        import sys
        import subprocess
        if sys.platform.startswith('win'):
            os.startfile(pdf_path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', pdf_path])
        else:
            subprocess.Popen(['xdg-open', pdf_path])

    def go_back(self, instance):
        self.manager.current = 'product_list'
