import os
os.environ["KIVY_GL_BACKEND"] = "sdl2"
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.data_cache import cache
from screens.credits_screen import CreditsScreen
# from screens.main_menu import MainMenu  # Ya no se usa
# Eliminamos type_screen y copies_screen del flujo
# from screens.type_screen import TypeScreen
# from screens.copies_screen import CopiesScreen
# from screens.total_screen import TotalScreen  # Ya no se usa
from screens.confirm_screen import ConfirmScreen
from screens.monedas_screen import MonedasScreen
from screens.done_screen import DoneScreen
from screens.historial_screen import HistorialScreen
from screens.transacciones_screen import TransaccionesScreen
from screens.deudores_screen import DeudoresScreen
from screens.product_manager_screen import ProductManagerScreen
from screens.product_list_screen import ProductListScreen
from screens.add_product_screen import AddProductScreen
from screens.caja_screen import CajaScreen
from kivy.config import Config
from kivy.core.window import Window


Window.clearcolor = (0.8, 0.9, 1, 1)
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '800')

class PrintApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(CreditsScreen(name='credits'))
        # sm.add_widget(MainMenu(name='main_menu'))  # Ya no se usa
        # Eliminamos type y copies del flujo
        # sm.add_widget(TypeScreen(name='type'))
        # sm.add_widget(CopiesScreen(name='copies'))
        # sm.add_widget(TotalScreen(name='total'))  # Ya no se usa
        sm.add_widget(ConfirmScreen(name='confirm'))
        sm.add_widget(DoneScreen(name='done'))
        sm.add_widget(HistorialScreen(name='historial'))
        sm.add_widget(TransaccionesScreen(name='transacciones'))
        sm.add_widget(MonedasScreen(name='monedas'))
        sm.add_widget(DeudoresScreen(name='deudores'))
        sm.add_widget(ProductManagerScreen(name='product_manager'))
        sm.add_widget(ProductListScreen(name='product_list'))
        sm.add_widget(AddProductScreen(name='add_product'))
        sm.add_widget(CajaScreen(name='caja'))
        sm.current = 'credits'  # Iniciar con la pantalla de créditos
        
        # Inicializar variables para el carrito de compra
        self.shopping_cart = {}  # {product_index: quantity}
        self.products_list = []
        
        return sm
    
    def reset_all_data(self):
        """Función centralizada para limpiar todos los datos y formularios"""
        # Limpiar variables del nuevo sistema de carrito
        self.shopping_cart = {}
        self.products_list = []
        
        # Limpiar cache si es necesario (opcional - solo en casos de problemas)
        # cache.clear_cache()  # Descomentaar solo si hay problemas de memoria
        
        print("🧹 Datos de la aplicación limpiados")
        
        # Limpiar variables antiguas (compatibilidad)
        if hasattr(self, 'selected_copies'):
            self.selected_copies = 0
        if hasattr(self, 'selected_type'):
            self.selected_type = ''
        if hasattr(self, 'selected_price'):
            self.selected_price = 0.0
        if hasattr(self, 'selected_printer'):
            self.selected_printer = ''
        if hasattr(self, 'selected_job'):
            self.selected_job = ''
        if hasattr(self, 'selected_file'):
            self.selected_file = None
        if hasattr(self, 'selected_sysname'):
            self.selected_sysname = ''
        
        # Limpiar pantalla de confirmación
        try:
            confirm = self.root.get_screen('confirm')
            confirm.name_input.text = ''
            confirm.group_input.text = ''
            confirm.pago_input.text = ''
            confirm.operacion_label.text = '0.00 - 0.00 = 0.00'
            confirm.cambio_label.text = 'Cambio = $0.00'
            confirm.info_label.text = ''
            if hasattr(confirm, 'feedback_label'):
                confirm.feedback_label.text = ''
        except Exception:
            pass
        
        # Limpiar pantalla de lista de productos
        try:
            product_list = self.root.get_screen('product_list')
            product_list.cart = {}
            product_list.selected_product_index = None
            if hasattr(product_list, 'selected_product_label'):
                product_list.selected_product_label.text = "Selecciona un producto"
            if hasattr(product_list, 'total_label'):
                product_list.total_label.text = 'Total: $0.00'
            if hasattr(product_list, 'cart_layout'):
                product_list.cart_layout.clear_widgets()
            product_list.update_continue_btn()
            product_list.update_products_display()
        except Exception:
            pass
        
        # Limpiar pantalla de agregar producto
        try:
            product_manager = self.root.get_screen('product_manager')
            product_manager.clear_form()
            product_manager.setup_for_adding()
        except Exception:
            pass

        # Limpiar pantalla de caja
        try:
            caja = self.root.get_screen('caja')
            caja.saldo_actual = caja.cargar_saldo()
            caja.actualizar_saldo_display()
            if hasattr(caja, 'feedback_label'):
                caja.feedback_label.text = ''
        except Exception:
            pass

if __name__ == '__main__':
    PrintApp().run()