"""
Widget de Imagen Optimizada con Lazy Loading
Especialmente optimizado para Windows y sistemas de baja velocidad

Características:
- Lazy loading: solo carga imágenes cuando son visibles
- Cache de imágenes en memoria con límite
- Detección de imágenes faltantes
- Placeholder automático para imágenes que no cargan
- Redimensionamiento inteligente para ahorrar memoria
"""

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.resources import resource_find
import os
import threading
from PIL import Image as PILImage
import io

class OptimizedImage(Image):
    def __init__(self, lazy_load=True, max_size=(200, 200), **kwargs):
        # Configuración de optimización
        self.lazy_load = lazy_load
        self.max_size = max_size
        self.original_source = kwargs.get('source', '')
        self.is_loaded = False
        self.load_attempted = False
        
        # Establecer imagen por defecto mientras carga
        if lazy_load and self.original_source:
            kwargs['source'] = 'assets/default_photo.png'
        
        super().__init__(**kwargs)
        
        # Cache estático de imágenes (compartido entre instancias)
        if not hasattr(OptimizedImage, '_image_cache'):
            OptimizedImage._image_cache = {}
            OptimizedImage._cache_size = 0
            OptimizedImage._max_cache_size = 50  # Máximo 50 imágenes en cache
        
        # Si lazy loading está habilitado, programar la carga
        if lazy_load and self.original_source:
            # Verificar si la imagen ya está en cache
            if self.original_source in OptimizedImage._image_cache:
                self.source = self.original_source
                self.is_loaded = True
                print(f"⚡ Imagen desde cache: {os.path.basename(self.original_source)}")
            else:
                # Programar carga diferida
                Clock.schedule_once(self._lazy_load, 0.1)
    
    def _lazy_load(self, dt):
        """Cargar imagen de forma diferida en hilo separado"""
        if self.load_attempted:
            return
        
        self.load_attempted = True
        
        # Verificar si el archivo existe
        if not os.path.exists(self.original_source):
            print(f"⚠️ Imagen no encontrada: {self.original_source}")
            # Mantener imagen por defecto
            return
        
        # Cargar en hilo separado para no bloquear UI
        threading.Thread(
            target=self._load_optimized_image,
            daemon=True
        ).start()
    
    def _load_optimized_image(self):
        """Cargar y optimizar imagen en hilo separado"""
        try:
            # Verificar si ya está en cache
            if self.original_source in OptimizedImage._image_cache:
                Clock.schedule_once(lambda dt: self._apply_cached_image(), 0)
                return
            
            # Cargar y optimizar imagen con PIL
            with PILImage.open(self.original_source) as pil_image:
                # Convertir a RGB si es necesario
                if pil_image.mode in ('RGBA', 'LA'):
                    # Crear fondo blanco para transparencias
                    background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                    if pil_image.mode == 'RGBA':
                        background.paste(pil_image, mask=pil_image.split()[-1])
                    else:
                        background.paste(pil_image)
                    pil_image = background
                elif pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Redimensionar si es muy grande
                if pil_image.size[0] > self.max_size[0] or pil_image.size[1] > self.max_size[1]:
                    pil_image.thumbnail(self.max_size, PILImage.Resampling.LANCZOS)
                    print(f"🖼️ Imagen redimensionada: {os.path.basename(self.original_source)} -> {pil_image.size}")
                
                # Guardar imagen optimizada temporalmente
                optimized_path = f"temp_optimized_{os.path.basename(self.original_source)}"
                pil_image.save(optimized_path, 'JPEG', quality=85, optimize=True)
                
                # Agregar al cache
                self._add_to_cache(self.original_source, optimized_path)
                
                # Programar actualización en el hilo principal
                Clock.schedule_once(lambda dt: self._apply_optimized_image(optimized_path), 0)
                
        except Exception as e:
            print(f"❌ Error optimizando imagen {self.original_source}: {e}")
            # Mantener imagen por defecto en caso de error
    
    def _add_to_cache(self, original_path, optimized_path):
        """Agregar imagen al cache con gestión de memoria"""
        # Limpiar cache si está lleno
        if OptimizedImage._cache_size >= OptimizedImage._max_cache_size:
            # Eliminar las 10 imágenes más antiguas
            old_items = list(OptimizedImage._image_cache.items())[:10]
            for old_path, old_optimized in old_items:
                try:
                    if os.path.exists(old_optimized):
                        os.remove(old_optimized)
                    del OptimizedImage._image_cache[old_path]
                    OptimizedImage._cache_size -= 1
                    print(f"🗑️ Imagen eliminada del cache: {os.path.basename(old_path)}")
                except Exception as e:
                    print(f"⚠️ Error eliminando del cache: {e}")
        
        # Agregar nueva imagen al cache
        OptimizedImage._image_cache[original_path] = optimized_path
        OptimizedImage._cache_size += 1
        print(f"💾 Imagen agregada al cache: {os.path.basename(original_path)} ({OptimizedImage._cache_size}/{OptimizedImage._max_cache_size})")
    
    def _apply_cached_image(self):
        """Aplicar imagen desde cache"""
        if self.original_source in OptimizedImage._image_cache:
            cached_path = OptimizedImage._image_cache[self.original_source]
            if os.path.exists(cached_path):
                self.source = cached_path
                self.is_loaded = True
                print(f"⚡ Imagen aplicada desde cache: {os.path.basename(self.original_source)}")
    
    def _apply_optimized_image(self, optimized_path):
        """Aplicar imagen optimizada en el hilo principal"""
        if os.path.exists(optimized_path):
            self.source = optimized_path
            self.is_loaded = True
            print(f"✅ Imagen optimizada cargada: {os.path.basename(self.original_source)}")
        else:
            print(f"⚠️ Imagen optimizada no encontrada: {optimized_path}")
    
    @staticmethod
    def clear_cache():
        """Limpiar todo el cache de imágenes"""
        if hasattr(OptimizedImage, '_image_cache'):
            for original_path, optimized_path in OptimizedImage._image_cache.items():
                try:
                    if os.path.exists(optimized_path) and optimized_path.startswith('temp_optimized_'):
                        os.remove(optimized_path)
                except Exception as e:
                    print(f"⚠️ Error eliminando archivo temporal: {e}")
            
            OptimizedImage._image_cache.clear()
            OptimizedImage._cache_size = 0
            print("🧹 Cache de imágenes limpiado completamente")
    
    @staticmethod
    def get_cache_stats():
        """Obtener estadísticas del cache"""
        if hasattr(OptimizedImage, '_image_cache'):
            return {
                'cached_images': OptimizedImage._cache_size,
                'max_cache_size': OptimizedImage._max_cache_size,
                'cache_usage': f"{OptimizedImage._cache_size}/{OptimizedImage._max_cache_size}",
                'cached_files': list(OptimizedImage._image_cache.keys())
            }
        return {'cached_images': 0}

    def on_source(self, instance, value):
        """Override para manejar cambios de source"""
        # Si no es lazy loading, comportamiento normal
        if not self.lazy_load:
            return
        
        # Para lazy loading, actualizar original_source si es necesario
        if value != 'assets/default_photo.png' and not value.startswith('temp_optimized_'):
            self.original_source = value
            self.is_loaded = False
            self.load_attempted = False
            
            # Verificar cache primero
            if value in OptimizedImage._image_cache:
                self._apply_cached_image()
            else:
                Clock.schedule_once(self._lazy_load, 0.1)