from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from screens.topbar import TopBar
import os
import json

class ProductManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.products = []
        self.build_interface()
        
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(TopBar(show_back=True))
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        content_layout = BoxLayout(orientation='vertical', padding=[20, 10], spacing=20)
        
        title = Label(
            text='Gestión de Productos',
            font_size=24,
            size_hint_y=None,
            height=50,
            color=(0.2, 0.4, 0.6, 1),
            bold=True
        )
        content_layout.add_widget(title)
        
        add_btn = Button(
            text='+ Agregar Nuevo Producto',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True
        )
        add_btn.bind(on_release=self.go_add_product)
        content_layout.add_widget(add_btn)
        
        scroll = ScrollView()
        self.products_grid = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=[10, 10]
        )
        self.products_grid.bind(minimum_height=self.products_grid.setter('height'))
        scroll.add_widget(self.products_grid)
        content_layout.add_widget(scroll)
        
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.load_products()
    
    def load_products(self):
        self.products = []
        if os.path.exists('productos.json'):
            try:
                with open('productos.json', 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
            except Exception:
                self.products = []
        
        self.products_grid.clear_widgets()
        
        for idx, product in enumerate(self.products):
            product_item = self.create_product_item(product, idx)
            self.products_grid.add_widget(product_item)
        
        if not self.products:
            no_products = Label(
                text='No hay productos registrados.\nUsa el botón "Agregar Nuevo Producto".',
                font_size=16,
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            )
            self.products_grid.add_widget(no_products)
    
    def create_product_item(self, product, index):
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            spacing=15,
            padding=[15, 10]
        )
        
        with item_layout.canvas.before:
            Color(1, 1, 1, 1)
            item_bg = Rectangle(pos=item_layout.pos, size=item_layout.size)
        item_layout.bind(pos=lambda instance, value: setattr(item_bg, 'pos', value))
        item_layout.bind(size=lambda instance, value: setattr(item_bg, 'size', value))
        
        info_layout = BoxLayout(orientation='vertical', spacing=5)
        
        name_label = Label(
            text=product.get('name', 'Sin nombre'),
            font_size=18,
            color=(0.1, 0.1, 0.1, 1),
            bold=True,
            halign='left'
        )
        info_layout.add_widget(name_label)
        
        price_label = Label(
            text=f"${product.get('price', '0.00')}",
            font_size=16,
            color=(0.3, 0.6, 0.3, 1),
            halign='left'
        )
        info_layout.add_widget(price_label)
        
        item_layout.add_widget(info_layout)
        
        delete_btn = Button(
            text='Eliminar',
            size_hint_x=None,
            width=80,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        delete_btn.bind(on_release=lambda x: self.delete_product(index))
        item_layout.add_widget(delete_btn)
        
        return item_layout
    
    def go_add_product(self, instance):
        self.manager.current = 'add_product'
    
    def delete_product(self, index):
        if index >= len(self.products):
            return
            
        product = self.products[index]
        
        content = BoxLayout(orientation='vertical', spacing=20, padding=[20, 20])
        
        message = Label(
            text=f'¿Eliminar "{product.get("name", "Sin nombre")}"?',
            font_size=16,
            halign='center'
        )
        content.add_widget(message)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=50)
        
        cancel_btn = Button(text='Cancelar', background_color=(0.6, 0.6, 0.6, 1))
        confirm_btn = Button(text='Eliminar', background_color=(0.8, 0.3, 0.3, 1))
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(confirm_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Confirmar eliminación',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda x: self.confirm_delete(index, popup))
        
        popup.open()
    
    def confirm_delete(self, index, popup):
        try:
            products = []
            if os.path.exists('productos.json'):
                with open('productos.json', 'r', encoding='utf-8') as f:
                    products = json.load(f)
            
            if index < len(products):
                del products[index]
                
                with open('productos.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                popup.dismiss()
                self.load_products()
                
                try:
                    self.manager.get_screen('product_list').load_products()
                except Exception:
                    pass
                
        except Exception as e:
            popup.dismiss()
            print(f"Error: {e}")
    
    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
