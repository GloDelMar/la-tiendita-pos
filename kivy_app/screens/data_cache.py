"""
Sistema de Cache Centralizado para Optimización de Rendimiento
Especialmente optimizado para Windows y sistemas de baja velocidad

Características:
- Cache en memoria para productos, deudores, transacciones
- Lazy loading de imágenes
- Detección de cambios en archivos
- Limpieza automática de cache
"""

import json
import csv
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading

class DataCache:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.products_cache = None
        self.products_mtime = 0
        self.deudores_cache = None
        self.deudores_mtime = 0
        self.saldo_cache = None
        self.saldo_mtime = 0
        
        # Cache para imágenes
        self.image_cache = {}
        self.image_cache_size = 50  # Máximo 50 imágenes en cache
        
        # Archivos a monitorear
        self.productos_file = "productos.json"
        self.deudores_file = "deudores.json" 
        self.saldo_file = "saldo_caja.txt"
        
        print("🚀 DataCache inicializado - optimización activa")
    
    def _get_file_mtime(self, filepath: str) -> float:
        """Obtener tiempo de modificación del archivo"""
        try:
            return os.path.getmtime(filepath)
        except (OSError, FileNotFoundError):
            return 0
    
    def _is_cache_valid(self, cache_mtime: float, filepath: str) -> bool:
        """Verificar si el cache sigue siendo válido"""
        return cache_mtime >= self._get_file_mtime(filepath)
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Obtener productos con cache inteligente"""
        current_mtime = self._get_file_mtime(self.productos_file)
        
        if (self.products_cache is None or 
            not self._is_cache_valid(self.products_mtime, self.productos_file)):
            
            try:
                with open(self.productos_file, 'r', encoding='utf-8') as f:
                    self.products_cache = json.load(f)
                self.products_mtime = current_mtime
                print(f"📦 Productos cargados desde archivo ({len(self.products_cache)} items)")
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                self.products_cache = []
                print("⚠️ Error cargando productos, usando lista vacía")
        else:
            print(f"⚡ Productos desde cache ({len(self.products_cache)} items)")
            
        return self.products_cache.copy()
    
    def save_products(self, products: List[Dict[str, Any]]) -> bool:
        """Guardar productos y actualizar cache"""
        try:
            with open(self.productos_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            # Actualizar cache
            self.products_cache = products.copy()
            self.products_mtime = self._get_file_mtime(self.productos_file)
            print(f"💾 Productos guardados y cache actualizado ({len(products)} items)")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error guardando productos: {e}")
            return False
    
    def get_deudores(self) -> List[Dict[str, Any]]:
        """Obtener deudores con cache inteligente"""
        current_mtime = self._get_file_mtime(self.deudores_file)
        
        if (self.deudores_cache is None or 
            not self._is_cache_valid(self.deudores_mtime, self.deudores_file)):
            
            try:
                with open(self.deudores_file, 'r', encoding='utf-8') as f:
                    self.deudores_cache = json.load(f)
                self.deudores_mtime = current_mtime
                print(f"👥 Deudores cargados desde archivo ({len(self.deudores_cache)} items)")
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                self.deudores_cache = []
                print("⚠️ Error cargando deudores, usando lista vacía")
        else:
            print(f"⚡ Deudores desde cache ({len(self.deudores_cache)} items)")
            
        return self.deudores_cache.copy()
    
    def save_deudores(self, deudores: List[Dict[str, Any]]) -> bool:
        """Guardar deudores y actualizar cache"""
        try:
            with open(self.deudores_file, 'w', encoding='utf-8') as f:
                json.dump(deudores, f, ensure_ascii=False, indent=2)
            
            # Actualizar cache
            self.deudores_cache = deudores.copy()
            self.deudores_mtime = self._get_file_mtime(self.deudores_file)
            print(f"💾 Deudores guardados y cache actualizado ({len(deudores)} items)")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error guardando deudores: {e}")
            return False
    
    def get_saldo(self) -> float:
        """Obtener saldo con cache inteligente"""
        current_mtime = self._get_file_mtime(self.saldo_file)
        
        if (self.saldo_cache is None or 
            not self._is_cache_valid(self.saldo_mtime, self.saldo_file)):
            
            try:
                with open(self.saldo_file, 'r', encoding='utf-8') as f:
                    saldo_text = f.read().strip()
                    # Extraer número del formato "$123.45"
                    if saldo_text.startswith('$'):
                        self.saldo_cache = float(saldo_text[1:])
                    else:
                        self.saldo_cache = float(saldo_text)
                self.saldo_mtime = current_mtime
                print(f"💰 Saldo cargado desde archivo: ${self.saldo_cache:.2f}")
            except (FileNotFoundError, ValueError, IOError):
                self.saldo_cache = 0.0
                print("⚠️ Error cargando saldo, usando $0.00")
        else:
            print(f"⚡ Saldo desde cache: ${self.saldo_cache:.2f}")
            
        return self.saldo_cache
    
    def save_saldo(self, saldo: float) -> bool:
        """Guardar saldo y actualizar cache"""
        try:
            with open(self.saldo_file, 'w', encoding='utf-8') as f:
                f.write(f"${saldo:.2f}")
            
            # Actualizar cache
            self.saldo_cache = saldo
            self.saldo_mtime = self._get_file_mtime(self.saldo_file)
            print(f"💾 Saldo guardado y cache actualizado: ${saldo:.2f}")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error guardando saldo: {e}")
            return False
    
    def append_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Agregar transacción al CSV de forma optimizada"""
        try:
            file_exists = os.path.exists("transacciones.csv")
            
            with open("transacciones.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Escribir header solo si el archivo es nuevo
                if not file_exists:
                    writer.writerow(["fecha", "hora", "productos", "total", "pago", "cambio", "tipo"])
                
                # Escribir la transacción
                writer.writerow([
                    transaction_data.get("fecha", ""),
                    transaction_data.get("hora", ""),
                    transaction_data.get("productos", ""),
                    transaction_data.get("total", "0.00"),
                    transaction_data.get("pago", "0.00"),
                    transaction_data.get("cambio", "0.00"),
                    transaction_data.get("tipo", "venta")
                ])
            
            print(f"📊 Transacción agregada: ${transaction_data.get('total', '0.00')}")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error guardando transacción: {e}")
            return False
    
    def append_cash_history(self, operation_data: Dict[str, Any]) -> bool:
        """Agregar operación de caja al historial"""
        try:
            file_exists = os.path.exists("historial_caja.csv")
            
            with open("historial_caja.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Escribir header solo si el archivo es nuevo
                if not file_exists:
                    writer.writerow(["fecha", "hora", "tipo", "monto", "saldo_anterior", "saldo_nuevo", "descripcion"])
                
                # Escribir la operación
                writer.writerow([
                    operation_data.get("fecha", ""),
                    operation_data.get("hora", ""),
                    operation_data.get("tipo", ""),
                    operation_data.get("monto", "0.00"),
                    operation_data.get("saldo_anterior", "0.00"),
                    operation_data.get("saldo_nuevo", "0.00"),
                    operation_data.get("descripcion", "")
                ])
            
            print(f"🏦 Operación de caja registrada: {operation_data.get('tipo', 'N/A')}")
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error guardando historial de caja: {e}")
            return False
    
    def clear_cache(self):
        """Limpiar todo el cache para forzar recarga"""
        self.products_cache = None
        self.products_mtime = 0
        self.deudores_cache = None
        self.deudores_mtime = 0
        self.saldo_cache = None
        self.saldo_mtime = 0
        print("🧹 Cache limpiado - próximas cargas desde archivo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache para debugging"""
        return {
            "products_cached": self.products_cache is not None,
            "products_count": len(self.products_cache) if self.products_cache else 0,
            "deudores_cached": self.deudores_cache is not None,
            "deudores_count": len(self.deudores_cache) if self.deudores_cache else 0,
            "saldo_cached": self.saldo_cache is not None,
            "saldo_value": self.saldo_cache,
            "image_cache_count": len(self.image_cache)
        }

# Instancia singleton global
cache = DataCache()