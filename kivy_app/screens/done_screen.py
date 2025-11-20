from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from screens.topbar import TopBar

class DoneScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Construir la interfaz
        try:
            self.build_interface()
            print("✅ DoneScreen construida correctamente")
        except Exception as e:
            print(f"❌ Error construyendo DoneScreen: {e}")
            # Interfaz mínima de emergencia
            self.add_widget(Label(text="Error en DoneScreen", color=(1,0,0,1)))
    
    def optimized_continue_selling(self):
        """Versión ultra-optimizada del botón continuar vendiendo con reinicio completo."""
        print("⚡ CONTINUANDO VENTA - Ultra optimizado")
        
        # 1. Obtener app de forma directa
        from kivy.app import App
        app = App.get_running_app()
        if not app:
            return False
        
        # 2. Limpieza crítica super-rápida - solo lo esencial
        # CONFIRM SCREEN - Batch directo
        try:
            confirm = app.root.get_screen('confirm')
            # Reset directo sin verificaciones
            confirm.pago_input.text = ''
            confirm.operacion_label.text = '0.00 - 0.00 = 0.00'
            confirm.cambio_label.text = 'Cambio = $0.00'
            confirm.info_label.text = ''
        except:
            pass
        
        # PRODUCT LIST SCREEN - Reset directo crítico
        try:
            product_list = app.root.get_screen('product_list')
            # Variables críticas - reset directo
            product_list.cart = {}
            product_list.selected_product_index = None
            
            # UI crítica - reset directo
            product_list.selected_product_label.text = 'Selecciona un producto'
            product_list.total_label.text = 'Total: $0.00'
            
            # Limpieza visual crítica
            product_list.cart_layout.clear_widgets()
            product_list.update_continue_btn()
            
            # Reset visual de tarjetas de productos (eliminar pintado/selección)
            try:
                if hasattr(product_list, '_product_cards'):
                    for card in product_list._product_cards:
                        # Resetear la cantidad a 0 para eliminar el color verde
                        card.quantity = 0
                        card.update_selection_style()
            except:
                pass
            
            # Reset cache de tarjetas para fresh display y forzar actualización visual
            try:
                del product_list._product_cards
            except:
                pass
                
        except:
            pass
        
        return True

    def build_interface(self):
        """Construir la interfaz de la pantalla done"""
        from kivy.app import App
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.uix.image import Image
        from kivy.uix.button import Button
        from kivy.metrics import dp

        root = BoxLayout(orientation='vertical')
        root.add_widget(TopBar(show_back=True))
        content = BoxLayout(orientation='vertical', spacing=30, padding=[40,60,40,60], size_hint_y=0.82)

        # Imagen centrada arriba del texto
        sello = Image(source='assets/sello_terminado.png', size_hint=(None, None), size=(160, 160), allow_stretch=True)
        sello_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        sello_anchor.add_widget(sello)
        content.add_widget(sello_anchor)

        # Texto
        content.add_widget(Label(text="Transacción finalizada", font_size=28, color=(0.1,0.2,0.4,1)))

        # Botón verde estilo app reutilizable
        class StyledButton(Button):
            def __init__(self, color_rgba, **kwargs):
                super().__init__(**kwargs)
                self.background_normal = ''
                self.background_color = color_rgba
                self.color = (1,1,1,1)
                self.font_size = 22
                self.size_hint = (None, None)
                self.height = 54
                self.padding = [24, 12]
                self.background_down = ''
                self.bind(texture_size=self._update_width)
                with self.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(*color_rgba)
                    self._rounded_rect = RoundedRectangle(radius=[18], pos=self.pos, size=self.size)
                self.bind(pos=self._update_rect, size=self._update_rect)
            def _update_width(self, *a):
                self.width = self.texture_size[0] + 48
            def _update_rect(self, *a):
                self._rounded_rect.pos = self.pos
                self._rounded_rect.size = self.size

        # Botón regresar a lista de productos centrado (rojo) - REINICIO COMPLETO OPTIMIZADO
        def reset_all_inputs(instance):
            """Función del botón continuar vendiendo - REINICIO TOTAL SIN CRÉDITOS"""
            
            print("🚀 Botón 'Continuar vendiendo' presionado - iniciando reinicio total")
            
            # Usar función optimizada de limpieza completa
            if self.optimized_continue_selling():
                # 3. Navegación inmediata - sin delays
                try:
                    self.manager.current = 'product_list'
                    print("✅ Navegación ultra-rápida completada")
                except Exception as e:
                    print(f"⚠️ Error en navegación: {e}")
        
        btn = StyledButton((0.85, 0.2, 0.2, 1), text='Continuar vendiendo', on_press=reset_all_inputs)
        btn_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        btn_anchor.add_widget(btn)
        content.add_widget(btn_anchor)

        root.add_widget(content)
        self.add_widget(root)

    def imprimir_recibo(self, instance):
        from kivy.app import App
        import os, subprocess
        app = App.get_running_app()
        pdf_path = getattr(app, 'pdf_ticket_path', None)
        printer = getattr(app, 'selected_printer', None)
        if pdf_path and os.path.exists(pdf_path):
            try:
                if printer:
                    subprocess.Popen(['lpr', '-P', printer, pdf_path])
                else:
                    subprocess.Popen(['lpr', pdf_path])
            except Exception as e:
                print(f"Error al imprimir el recibo: {e}")
        else:
            print("No hay recibo para imprimir.")