from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
import platform
try:
    from plyer import share
except ImportError:
    share = None

class ImageButton(ButtonBehavior, Image):
    pass
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from screens.topbar import TopBar
from screens.proportional_image import ProportionalImage
from screens.data_cache import cache
from datetime import datetime
import os, csv

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

class ConfirmScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar(show_back=True))
        content = BoxLayout(orientation='vertical', spacing=20, padding=[30, 0, 30, 20], size_hint_y=0.92)  # Aumentado size_hint_y para mover contenido más arriba

        # Sección de información de productos (más compacta)
        info_section = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=120)  # Reducido de 150 a 120
        
        # Título de productos más pequeño
        productos_title = Label(
            text='[b][color=#2E7D32]PRODUCTOS SELECCIONADOS[/color][/b]', 
            font_size=18,  # Reducido de 24 a 18
            markup=True, 
            size_hint=(1, None), 
            height=25,     # Reducido de 30 a 25
            halign='center'
        )
        productos_title.bind(size=productos_title.setter('text_size'))
        
        # Info de productos con fondo
        from kivy.graphics import Color, Rectangle, RoundedRectangle
        self.info_label = Label(
            text='', 
            font_size=14,  # Reducido de 18 a 14
            color=(0.2,0.2,0.2,1), 
            size_hint=(1, None), 
            height=90,     # Reducido de 110 a 90
            halign='left',  # Cambio a izquierda para mejor legibilidad
            valign='top'    # Cambio a arriba para mejor distribución
        )
        # Configurar text_size inicial para wrapping
        self.info_label.bind(size=self._update_info_text_size)
        
        # Agregar fondo redondeado al info_label
        with self.info_label.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.info_bg = RoundedRectangle(pos=self.info_label.pos, size=self.info_label.size, radius=[10])
            Color(0.8, 0.8, 0.8, 1)
            from kivy.graphics import Line
            self.info_border = Line(rounded_rectangle=(self.info_label.x, self.info_label.y, self.info_label.width, self.info_label.height, 10), width=2)
        
        def update_info_bg(*args):
            self.info_bg.pos = self.info_label.pos
            self.info_bg.size = self.info_label.size
            self.info_border.rounded_rectangle = (self.info_label.x, self.info_label.y, self.info_label.width, self.info_label.height, 10)
        
        self.info_label.bind(pos=update_info_bg, size=update_info_bg)
        
        info_section.add_widget(productos_title)
        info_section.add_widget(self.info_label)
        content.add_widget(info_section)

        # Espaciador más pequeño entre secciones
        content.add_widget(BoxLayout(size_hint_y=None, height=15))  # Reducido de 25 a 15

        # Sección de monto a cobrar (centrado y más compacto)
        monto_section = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=45)  # Reducido de 60 a 45
        
        monto_label = Label(
            text='[b][color=#1976D2]MONTO A COBRAR: $0.00[/color][/b]',
            font_size=24,  # Reducido de 32 a 24
            markup=True,
            size_hint=(1, None),
            height=40,     # Reducido de 50 a 40
            halign='center',
            valign='middle'
        )
        monto_label.bind(size=monto_label.setter('text_size'))
        monto_section.add_widget(monto_label)
        self.monto_label = monto_label  # Guardar referencia para actualizar
        content.add_widget(monto_section)

        # Espaciador más pequeño
        content.add_widget(BoxLayout(size_hint_y=None, height=10))  # Reducido de 20 a 10

        # Sección principal (izquierda: pago y botones, derecha: pizarra) más compacta
        main_section = BoxLayout(orientation='horizontal', spacing=30, size_hint=(1, None), height=180)  # Reducido spacing de 50 a 30 y height de 200 a 180
        
        # Columna izquierda: Campo de pago y botones
        left_col = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.5, 1))
        
        # Campo de pago más compacto
        pago_container = BoxLayout(orientation='horizontal', spacing=8, size_hint=(1, None), height=40)  # Reducido height de 50 a 40
        
        self.pago_input = TextInput(
            hint_text='¿Con cuánto paga?', 
            font_size=18,  # Reducido de 22 a 18
            size_hint=(1, None), 
            height=40,     # Reducido de 50 a 40
            multiline=False, 
            input_filter='float',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            cursor_color=(0.2, 0.6, 1, 1),
            padding=[10, 10]  # Reducido padding de 15 a 10
        )
        self.pago_input.bind(text=self.on_pago_changed)
        
        # Botón de monedas más pequeño
        btn_monedas = ImageButton(
            source='assets/idea.png', 
            size_hint=(None, None), 
            size=(40, 40)  # Reducido de 50 a 40
        )
        
        def go_to_monedas_screen(instance):
            from kivy.app import App
            app = App.get_running_app()
            app.root.current = 'monedas'
        btn_monedas.bind(on_release=go_to_monedas_screen)
        
        pago_container.add_widget(self.pago_input)
        pago_container.add_widget(btn_monedas)
        
        # Espaciador
        spacer = BoxLayout(size_hint=(1, 0.2))
        
        # Sección de botones Sí/No más compacta
        from kivy.uix.anchorlayout import AnchorLayout
        btns_container = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, None), height=100)  # Reducido height de 120 a 100
        
        # Título de confirmación más pequeño
        label_pagado = Label(
            text='[b][color=#D32F2F]¿PAGADO?[/color][/b]', 
            font_size=18,  # Reducido de 24 a 18
            markup=True, 
            size_hint=(1, None), 
            height=30,     # Reducido de 35 a 30
            halign='center', 
            valign='middle'
        )
        label_pagado.bind(size=label_pagado.setter('text_size'))
        
        # Botones Sí y No más pequeños
        btns_center = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=50)  # Reducido de 60 a 50
        btns_inner = BoxLayout(orientation='horizontal', spacing=30, size_hint=(None, None), size=(110, 50))  # Reducido spacing y tamaño
        
        btn_yes = ImageButton(
            source='assets/yes_btn.png', 
            size_hint=(None, None), 
            size=(50, 50)  # Reducido de 60 a 50
        )
        btn_yes.bind(on_release=lambda inst: self.finish(True))
        
        btn_no = ImageButton(
            source='assets/no_btn.png', 
            size_hint=(None, None), 
            size=(50, 50)  # Reducido de 60 a 50
        )
        btn_no.bind(on_release=lambda inst: self.finish(False))
        
        btns_inner.add_widget(btn_yes)
        btns_inner.add_widget(btn_no)
        btns_center.add_widget(btns_inner)
        
        btns_container.add_widget(label_pagado)
        btns_container.add_widget(btns_center)
        
        # Agregar elementos a la columna izquierda
        left_col.add_widget(pago_container)
        left_col.add_widget(spacer)
        left_col.add_widget(btns_container)
        
        # Columna derecha: Pizarra (sin leyenda "CÁLCULO")
        from kivy.uix.popup import Popup
        from kivy.uix.image import Image
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.button import Button as KivyButton
        right_col = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.5, 1))
        
        # Área de pizarra sin título
        pizarra_area = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        
        with pizarra_area.canvas.before:
            from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
            Color(0.15, 0.35, 0.15, 1)  # Verde pizarrón
            self._chalk_bg = RoundedRectangle(pos=pizarra_area.pos, size=pizarra_area.size, radius=[15])
            Color(1, 1, 1, 0.8)
            self._chalk_border = Line(rounded_rectangle=(pizarra_area.x, pizarra_area.y, pizarra_area.width, pizarra_area.height, 15), width=3)
        
        from kivy.app import App
        app = App.get_running_app()
        total = 0
        
        # Etiqueta de operación más pequeña
        self.operacion_label = Label(
            text=f"0.00 - {total:.2f} = 0.00", 
            font_size=16,  # Reducido de 18 a 16
            color=(1,1,1,1), 
            size_hint=(1, None), 
            height=40,     # Reducido de 50 a 40
            halign='center',
            valign='middle'
        )
        self.operacion_label.bind(size=self.operacion_label.setter('text_size'))
        
        # Fila de cambio más compacta
        cambio_row = BoxLayout(orientation='horizontal', spacing=8, size_hint=(1, None), height=60, padding=[8, 0])  # Reducido height y padding
        
        # Etiqueta "Cambio:" más pequeña
        cambio_label_text = Label(
            text='Cambio:', 
            font_size=16,  # Reducido de 20 a 16
            color=(1,1,1,1), 
            size_hint=(None, 1), 
            width=70,      # Reducido de 80 a 70
            halign='center'
        )
        
        self.cambio_label = Label(
            text='$0.00', 
            font_size=22,  # Reducido de 28 a 22
            color=(1,1,0.2,1),  # Amarillo para destacar
            size_hint=(1, 1),
            halign='center',
            valign='middle',
            bold=True
        )
        self.cambio_label.bind(size=self.cambio_label.setter('text_size'))
        
        btn_cambio = ImageButton(source='assets/idea.png', size_hint=(None, None), size=(35, 35))  # Reducido de 40 a 35

        def open_cambio_popup(instance):
            monedas = [200, 100, 50, 20, 10, 5, 2, 1]
            img_map = {0.5:'m_050.png', 1:'m_1.png', 2:'m_2.png', 5:'m_5.png', 10:'m_10.png', 20:'b_20.png', 50:'b_50.png', 100:'b_100.png', 200:'b_200.png'}
            try:
                cambio = float(self.cambio_label.text.replace('$','').strip())
            except:
                cambio = 0.0
            opciones = []
            def encontrar_combinaciones(restante, actual, idx):
                if abs(restante) < 0.01:
                    opciones.append(list(actual))
                    return
                for i in range(idx, len(monedas)):
                    m = monedas[i]
                    if m <= restante + 0.001:
                        actual.append(m)
                        encontrar_combinaciones(round(restante-m,2), actual, i)
                        actual.pop()
            if cambio > 0:
                encontrar_combinaciones(round(cambio, 2), [], 0)
                layout = BoxLayout(orientation='vertical', spacing=16, padding=16, size_hint_y=None)
                if not opciones:
                    layout.add_widget(Label(text='No hay combinaciones para este cambio', font_size=18))
                else:
                    layout.bind(minimum_height=layout.setter('height'))
                    for comb in opciones:
                        if 0.5 in comb:
                            continue
                        if len(comb) > 10:
                            continue
                        from kivy.uix.boxlayout import BoxLayout as KivyBox
                        from kivy.graphics import Color, Line, Rectangle
                        class ComboBox(KivyBox):
                            def __init__(self, **kwargs):
                                super().__init__(**kwargs)
                                with self.canvas.before:
                                    Color(0.96, 0.96, 0.96, 1)
                                    self.bg = Rectangle(pos=self.pos, size=self.size)
                                    Color(0.10, 0.46, 0.82, 1)
                                    self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
                                self.bind(pos=self._update_rect, size=self._update_rect)
                            def _update_rect(self, *a):
                                self.bg.pos = self.pos
                                self.bg.size = self.size
                                self.border.rectangle = (self.x, self.y, self.width, self.height)
                        combo_box = ComboBox(orientation='horizontal', spacing=10, size_hint_y=None, height=90, padding=10)
                        for m in comb:
                            img_path = f"assets/{img_map[m]}" if m in img_map else ''
                            img = Image(source=img_path, size_hint=(None, None), size=(60,60))
                            combo_box.add_widget(img)
                        layout.add_widget(combo_box)
                scroll = ScrollView(size_hint=(1, 1))
                scroll.add_widget(layout)
                popup = Popup(title='Opciones de cambio', content=scroll, size_hint=(0.95, 0.7))
                popup.open()
        btn_cambio.bind(on_release=open_cambio_popup)
        
        cambio_row.add_widget(cambio_label_text)
        cambio_row.add_widget(self.cambio_label)
        cambio_row.add_widget(btn_cambio)
        
        pizarra_area.add_widget(self.operacion_label)
        pizarra_area.add_widget(cambio_row)
        
        right_col.add_widget(pizarra_area)
        
        def update_chalkboard(*a):
            self._chalk_bg.pos = pizarra_area.pos
            self._chalk_bg.size = pizarra_area.size
            self._chalk_border.rounded_rectangle = (pizarra_area.x, pizarra_area.y, pizarra_area.width, pizarra_area.height, 15)
        pizarra_area.bind(pos=update_chalkboard, size=update_chalkboard)

        main_section.add_widget(left_col)
        main_section.add_widget(right_col)
        content.add_widget(main_section)

        self.add_widget(root)
        root.add_widget(content)

    def _update_info_text_size(self, instance, size):
        """Actualiza el text_size del info_label para wrapping automático"""
        self.info_label.text_size = (self.info_label.width - 40, None)

    def on_pre_enter(self, *args):
        from kivy.app import App
        app = App.get_running_app()
        
        # Calcular total del carrito
        total = 0
        if hasattr(app, 'shopping_cart') and hasattr(app, 'products_list'):
            for product_idx, quantity in app.shopping_cart.items():
                if product_idx < len(app.products_list):
                    price = float(app.products_list[product_idx]['price'])
                    total += price * quantity
        
        # Mostrar información de productos seleccionados
        products_info = []
        if hasattr(app, 'shopping_cart') and hasattr(app, 'products_list'):
            for product_idx, quantity in app.shopping_cart.items():
                if product_idx < len(app.products_list) and quantity > 0:
                    product = app.products_list[product_idx]
                    products_info.append(f"{product['name']} x{quantity}")
        
        products_text = "\n".join(products_info) if products_info else "Sin productos"
        self.info_label.text = f"Productos:\n{products_text}"
        # Ajustar text_size para usar todo el ancho disponible con más margen
        self.info_label.text_size = (self.info_label.width - 40, None)
        
        # Actualizar el monto a cobrar
        self.monto_label.text = f'[b][color=#1976D2]MONTO A COBRAR: ${total:.2f}[/color][/b]'
        
        if not self.pago_input.text:
            self.operacion_label.text = f"0.00 - {total:.2f} = 0.00"
            self.cambio_label.text = f"$0.00"
        else:
            try:
                pago = float(self.pago_input.text)
            except:
                pago = 0.0
            cambio = pago - total
            self.operacion_label.text = f"{pago:.2f} - {total:.2f} = {cambio:.2f}"
            self.cambio_label.text = f"${cambio:.2f}"

    def on_pago_changed(self, instance, value):
        from kivy.app import App
        app = App.get_running_app()
        
        # Calcular total del carrito
        total = 0
        if hasattr(app, 'shopping_cart') and hasattr(app, 'products_list'):
            for product_idx, quantity in app.shopping_cart.items():
                if product_idx < len(app.products_list):
                    price = float(app.products_list[product_idx]['price'])
                    total += price * quantity
        
        try:
            pago = float(value)
        except:
            pago = 0.0
        cambio = pago - total
        self.operacion_label.text = f"{pago:.2f} - {total:.2f} = {cambio:.2f}"
        self.cambio_label.text = f"${cambio:.2f}"
        
        # Actualizar el monto a cobrar también
        self.monto_label.text = f'[b][color=#1976D2]MONTO A COBRAR: ${total:.2f}[/color][/b]'

    def clear_all_data(self):
        """Limpia todos los datos del formulario de confirmación"""
        self.pago_input.text = ''
        self.info_label.text = ''
        self.operacion_label.text = "0.00 - 0.00 = 0.00"
        self.cambio_label.text = "$0.00"
        self.monto_label.text = '[b][color=#1976D2]MONTO A COBRAR: $0.00[/color][/b]'

    def save_transaction_json(self, transaction_data):
        """Guarda transacción detallada en archivo JSON"""
        import json
        import os
        
        json_file = 'transacciones.json'
        
        # Cargar transacciones existentes
        transactions = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
            except Exception as e:
                print(f"⚠️ Error al leer transacciones JSON: {e}")
                transactions = []
        
        # Agregar nueva transacción
        transactions.append(transaction_data)
        
        # Guardar archivo actualizado
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, ensure_ascii=False, indent=2)
            print(f"📊 Transacción detallada guardada en JSON")
        except Exception as e:
            print(f"❌ Error al guardar transacción JSON: {e}")

    def show_debtor_popup(self, total, productos_comprados, registro):
        """Muestra popup para agregar deudor cuando no se paga"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        
        # Crear contenido del popup
        content = BoxLayout(orientation='vertical', spacing=15, padding=[20, 20, 20, 20])
        
        # Título
        title_label = Label(
            text='[b][color=#D32F2F]AGREGAR DEUDOR[/color][/b]',
            markup=True,
            font_size=20,
            size_hint_y=None,
            height=40,
            halign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # Info de deuda
        debt_label = Label(
            text=f'Monto adeudado: ${total:.2f}',
            font_size=18,
            size_hint_y=None,
            height=30,
            color=(0.8, 0.2, 0.2, 1)
        )
        
        # Campo nombre
        name_label = Label(text='Nombre:', size_hint_y=None, height=30, halign='left')
        name_label.bind(size=name_label.setter('text_size'))
        name_input = TextInput(
            hint_text='Ingrese el nombre del deudor',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        
        # Campo grupo
        group_label = Label(text='Grupo:', size_hint_y=None, height=30, halign='left')
        group_label.bind(size=group_label.setter('text_size'))
        group_input = TextInput(
            hint_text='Ingrese el grupo del deudor',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        
        # Botones
        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=50)
        
        btn_cancel = Button(
            text='Cancelar',
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_add = Button(
            text='Agregar Deudor',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        buttons_layout.add_widget(btn_cancel)
        buttons_layout.add_widget(btn_add)
        
        # Agregar widgets al contenido
        content.add_widget(title_label)
        content.add_widget(debt_label)
        content.add_widget(name_label)
        content.add_widget(name_input)
        content.add_widget(group_label)
        content.add_widget(group_input)
        content.add_widget(buttons_layout)
        
        # Crear popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.7),
            auto_dismiss=False
        )
        
        def cancel_debt(instance):
            popup.dismiss()
            # Volver a la lista de productos sin guardar nada
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'reset_all_data'):
                app.reset_all_data()
            self.manager.current = 'product_list'
        
        def add_debt(instance):
            nombre = name_input.text.strip()
            grupo = group_input.text.strip()
            
            if not nombre or not grupo:
                # Mostrar mensaje de error si faltan datos
                error_popup = Popup(
                    title='Error',
                    content=Label(text='Por favor ingrese nombre y grupo'),
                    size_hint=(0.6, 0.4)
                )
                error_popup.open()
                return
            
            # Actualizar registro con datos del deudor
            registro['nombre'] = nombre
            registro['grupo'] = grupo
            
            # Continuar con el proceso de guardado
            self.save_transaction_and_continue(registro, productos_comprados, False)
            popup.dismiss()
        
        btn_cancel.bind(on_release=cancel_debt)
        btn_add.bind(on_release=add_debt)
        
        popup.open()

    def save_transaction_and_continue(self, registro, productos_comprados, pagado):
        """Guarda la transacción y continúa con el flujo"""
        from kivy.app import App
        import csv
        import os
        import json
        from datetime import datetime
        
        app = App.get_running_app()
        pdf_path = None
        
        # Generar PDF si está disponible
        if FPDF:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(40, 40, 40)
            logo_path = os.path.join('assets', 'cam15_logo.png')
            pdf.set_xy(40, 40)
            pdf.image(logo_path, x=40, y=40, w=pdf.w*0.3-40, h=30, type='', link='')
            x_right = 40 + (pdf.w-80)*0.3
            pdf.set_xy(x_right, 40)
            pdf.set_font('Arial', 'B', 13)
            pdf.cell((pdf.w-80)*0.7, 10, 'CENTRO DE ATENCIÓN MÚLTIPLE #15', 0, 2, 'L')
            pdf.set_font('Arial', '', 12)
            pdf.cell((pdf.w-80)*0.7, 8, 'CCT 18DML0015G', 0, 2, 'L')
            pdf.cell((pdf.w-80)*0.7, 8, 'TALLER DE FORMACIÓN LABORAL', 0, 2, 'L')
            pdf.set_y(40+30+20)
            import glob
            now = datetime.now()
            mes = now.strftime('%m')
            recibos = glob.glob('recibo_*.pdf')
            folios_mes = [f for f in recibos if f'recibo_{now.strftime("%Y-%m")}' in f]
            folio_num = len(folios_mes) + 1
            folio_str = f"{mes}-{folio_num:05d}"
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Folio: {folio_str}', 0, 1, 'R')
            pdf.set_font('Arial', '', 12)
            
            # Agregar información con nombre y grupo del deudor
            pdf.cell(0, 10, f'Fecha: {registro["fecha"]}', ln=1)
            pdf.cell(0, 10, f'Nombre: {registro["nombre"]}', ln=1)
            pdf.cell(0, 10, f'Grupo: {registro["grupo"]}', ln=1)
            pdf.cell(0, 10, '', ln=1)  # Línea en blanco
            
            # Agregar detalle de productos
            pdf.cell(0, 10, 'PRODUCTOS:', ln=1)
            for producto in productos_comprados:
                pdf.cell(0, 10, f"  {producto['nombre']} x{producto['cantidad']} = ${producto['subtotal']:.2f}", ln=1)
            
            pdf.cell(0, 10, '', ln=1)  # Línea en blanco
            pdf.cell(0, 10, f'Total: ${registro["total"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Pago: ${registro["pago"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Cambio: ${registro["cambio"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Pagado: {registro["pagado"]}', ln=1)
            
            fecha_safe = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            pdf_path = f"recibo_{fecha_safe}.pdf"
            pdf.output(pdf_path)
        
        app.pdf_ticket_path = pdf_path

        # Guardar en transacciones.csv usando cache optimizado
        cache.append_transaction(registro)
        
        # CREAR Y GUARDAR TRANSACCIÓN DETALLADA EN JSON PARA DEUDORES
        transaction_json_deudor = {
            'fecha': registro['fecha'],
            'cliente': registro['nombre'],
            'grupo': registro['grupo'],
            'productos': productos_comprados,  # Lista detallada de productos
            'total': registro['total'],
            'pago': registro['pago'],
            'cambio': registro['cambio'],
            'pagado': registro['pagado']
        }
        self.save_transaction_json(transaction_json_deudor)

        # Agregar a deudores si no está pagado - OPTIMIZADO CON CACHE
        if not pagado and registro['nombre'] and registro['grupo']:
            # Cargar deudores existentes usando cache optimizado
            deudores_data = cache.get_deudores()
            
            # Buscar si el deudor ya existe
            deudor_existente = None
            for deudor in deudores_data:
                if deudor['nombre'] == registro['nombre'] and deudor['grupo'] == registro['grupo']:
                    deudor_existente = deudor
                    break
            
            if deudor_existente:
                # Actualizar deuda existente
                deudor_existente['deuda'] += registro['total']
                deudor_existente['ultima_compra'] = registro['fecha']
            else:
                # Crear nuevo deudor
                nuevo_deudor = {
                    'nombre': registro['nombre'],
                    'grupo': registro['grupo'],
                    'deuda': registro['total'],
                    'fecha_primera_deuda': registro['fecha'],
                    'ultima_compra': registro['fecha']
                }
                deudores_data.append(nuevo_deudor)
            
            # Guardar deudores actualizados usando cache optimizado
            cache.save_deudores(deudores_data)
        
        # Limpiar datos y continuar
        try:
            monedas_screen = app.root.get_screen('monedas')
            if hasattr(monedas_screen, 'clear_all_data'):
                monedas_screen.clear_all_data()
        except Exception:
            pass
        
        self.clear_all_data()
        
        # Limpiar carrito de la app
        if hasattr(app, 'shopping_cart'):
            app.shopping_cart = {}
        if hasattr(app, 'products_list'):
            app.products_list = []
            
        # Cuando se agrega un deudor (no pagado), siempre ir a 'done'
        self.manager.current = 'done'

    def finish(self, pagado):
        from kivy.app import App
        import json
        app = App.get_running_app()
        
        # Calcular total del carrito
        total = 0
        productos_comprados = []
        if hasattr(app, 'shopping_cart') and hasattr(app, 'products_list'):
            for product_idx, quantity in app.shopping_cart.items():
                if product_idx < len(app.products_list) and quantity > 0:
                    product = app.products_list[product_idx]
                    price = float(product['price'])
                    subtotal = price * quantity
                    total += subtotal
                    productos_comprados.append({
                        'nombre': product['name'],
                        'precio_unitario': price,
                        'cantidad': quantity,
                        'subtotal': subtotal
                    })
        
        nombre = ""  # Ya no se requiere nombre
        grupo = ""   # Ya no se requiere grupo
        pago = 0.0
        try: pago = float(self.pago_input.text)
        except: pass
        cambio = pago - total if pagado else 0.0
        # Eliminar validación de nombre y grupo - ya no son requeridos
        if pagado:
            self.cambio_label.text = f"{cambio:.2f}"
        else:
            self.cambio_label.text = ''
        
        # **AGREGAR EL DINERO A LA CAJA AUTOMÁTICAMENTE SI ESTÁ PAGADO**
        if pagado and total > 0:
            try:
                # Obtener la pantalla de caja
                caja_screen = self.manager.get_screen('caja')
                
                # Agregar la venta al saldo de caja
                caja_screen.agregar_venta(total)
                print(f"💰 VENTA AGREGADA A CAJA: ${total:.2f}")
                
            except Exception as e:
                print(f"❌ Error al agregar venta a caja: {e}")
        
        # Crear string con productos para el registro CSV (compatibilidad)
        productos_str = "; ".join([f"{p['nombre']} x{p['cantidad']}" for p in productos_comprados])
        
        # CREAR TRANSACCIÓN CON PRODUCTOS DETALLADOS PARA JSON
        transaction_json = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cliente': 'Cliente',  # Valor por defecto
            'grupo': 'General',   # Valor por defecto
            'productos': productos_comprados,  # Lista detallada de productos
            'total': total,
            'pago': pago,
            'cambio': cambio,
            'pagado': 'SI' if pagado else 'NO'
        }
        
        # REGISTRO CSV (compatibilidad hacia atrás)
        registro = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nombre': 'Cliente',  # Valor por defecto
            'grupo': 'General',   # Valor por defecto
            'productos': productos_str,
            'total': total,
            'pago': pago,
            'cambio': cambio,
            'pagado': 'SI' if pagado else 'NO',
        }
        pdf_path = None
        if FPDF:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(40, 40, 40)
            logo_path = os.path.join('assets', 'cam15_logo.png')
            pdf.set_xy(40, 40)
            pdf.image(logo_path, x=40, y=40, w=pdf.w*0.3-40, h=30, type='', link='')
            x_right = 40 + (pdf.w-80)*0.3
            pdf.set_xy(x_right, 40)
            pdf.set_font('Arial', 'B', 13)
            pdf.cell((pdf.w-80)*0.7, 10, 'CENTRO DE ATENCIÓN MÚLTIPLE #15', 0, 2, 'L')
            pdf.set_font('Arial', '', 12)
            pdf.cell((pdf.w-80)*0.7, 8, 'CCT 18DML0015G', 0, 2, 'L')
            pdf.cell((pdf.w-80)*0.7, 8, 'TALLER DE FORMACIÓN LABORAL', 0, 2, 'L')
            pdf.set_y(40+30+20)
            import glob
            now = datetime.now()
            mes = now.strftime('%m')
            recibos = glob.glob('recibo_*.pdf')
            folios_mes = [f for f in recibos if f'recibo_{now.strftime("%Y-%m")}' in f]
            folio_num = len(folios_mes) + 1
            folio_str = f"{mes}-{folio_num:05d}"
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Folio: {folio_str}', 0, 1, 'R')
            pdf.set_font('Arial', '', 12)
            
            # Agregar información básica (sin nombre y grupo)
            pdf.cell(0, 10, f'Fecha: {registro["fecha"]}', ln=1)
            pdf.cell(0, 10, '', ln=1)  # Línea en blanco
            
            # Agregar detalle de productos
            pdf.cell(0, 10, 'PRODUCTOS:', ln=1)
            for producto in productos_comprados:
                pdf.cell(0, 10, f"  {producto['nombre']} x{producto['cantidad']} = ${producto['subtotal']:.2f}", ln=1)
            
            pdf.cell(0, 10, '', ln=1)  # Línea en blanco
            pdf.cell(0, 10, f'Total: ${registro["total"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Pago: ${registro["pago"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Cambio: ${registro["cambio"]:.2f}', ln=1)
            pdf.cell(0, 10, f'Pagado: {registro["pagado"]}', ln=1)
            
            fecha_safe = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            pdf_path = f"recibo_{fecha_safe}.pdf"
            pdf.output(pdf_path)
        app.pdf_ticket_path = pdf_path

        # Guardar transacción usando cache optimizado (CSV)
        cache.append_transaction(registro)
        
        # GUARDAR TRANSACCIÓN DETALLADA EN JSON
        self.save_transaction_json(transaction_json)

        # Manejar deudores cuando no se paga
        if not pagado and total > 0:
            self.show_debtor_popup(total, productos_comprados, registro)
            return  # Salir aquí, el popup manejará el resto
        
        # Limpiar datos de monedas_screen al completar proceso
        try:
            monedas_screen = app.root.get_screen('monedas')
            if hasattr(monedas_screen, 'clear_all_data'):
                monedas_screen.clear_all_data()
        except Exception:
            pass
        
        # Limpiar datos de confirm_screen
        self.clear_all_data()
        
        # Limpiar carrito de la app
        if hasattr(app, 'shopping_cart'):
            app.shopping_cart = {}
        if hasattr(app, 'products_list'):
            app.products_list = []
            
        # Si pagó, ir a 'done'; si no pagó, ir a lista de productos (aunque esto no debería pasar aquí)
        self.manager.current = 'done' if pagado else 'product_list'