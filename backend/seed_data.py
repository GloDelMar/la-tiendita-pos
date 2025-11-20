"""
Script para insertar datos de prueba en Supabase
Ejecutar: python seed_data.py
"""
import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import supabase

def seed_products():
    """Insertar productos de prueba"""
    products = [
        {"name": "Coca Cola 600ml", "price": 1.50},
        {"name": "Pepsi 600ml", "price": 1.50},
        {"name": "Agua 500ml", "price": 0.75},
        {"name": "Galletas Oreo", "price": 2.00},
        {"name": "Pan Blanco", "price": 1.20},
        {"name": "Leche 1L", "price": 1.80},
        {"name": "Café Nescafé 100g", "price": 5.50},
        {"name": "Azúcar 1kg", "price": 2.30},
        {"name": "Arroz 1kg", "price": 1.90},
        {"name": "Aceite 900ml", "price": 3.50},
    ]
    
    try:
        response = supabase.table("products").insert(products).execute()
        print(f"✅ {len(products)} productos insertados correctamente")
        return response.data
    except Exception as e:
        print(f"❌ Error al insertar productos: {e}")
        return None

def seed_cash_initial():
    """Insertar saldo inicial de caja"""
    try:
        # Verificar si ya existe un saldo
        existing = supabase.table("cash_operations").select("*").limit(1).execute()
        if existing.data:
            print("ℹ️  Ya existe un saldo de caja, omitiendo inserción")
            return existing.data[0]
        
        # Crear saldo inicial
        initial_cash = {
            "tipo_operacion": "AJUSTE",
            "monto": 100.00,
            "saldo": 100.00,
            "descripcion": "Saldo inicial de caja"
        }
        response = supabase.table("cash_operations").insert(initial_cash).execute()
        print(f"✅ Saldo inicial de caja: ${response.data[0]['saldo']}")
        return response.data[0]
    except Exception as e:
        print(f"❌ Error al insertar saldo inicial: {e}")
        return None

def seed_sample_transaction():
    """Crear una transacción de ejemplo"""
    try:
        # Obtener algunos productos
        products = supabase.table("products").select("*").limit(3).execute()
        if not products.data:
            print("⚠️  No hay productos, primero ejecuta seed_products()")
            return None
        
        # Crear transacción
        transaction = {
            "cliente": "Cliente de Prueba",
            "grupo": "General",
            "productos": [
                {
                    "nombre": products.data[0]["name"],
                    "cantidad": 2,
                    "precio_unitario": products.data[0]["price"],
                    "subtotal": products.data[0]["price"] * 2
                },
                {
                    "nombre": products.data[1]["name"],
                    "cantidad": 1,
                    "precio_unitario": products.data[1]["price"],
                    "subtotal": products.data[1]["price"]
                }
            ],
            "total": (products.data[0]["price"] * 2) + products.data[1]["price"],
            "pago": (products.data[0]["price"] * 2) + products.data[1]["price"],
            "cambio": 0,
            "pagado": "SI"
        }
        
        response = supabase.table("transactions").insert(transaction).execute()
        
        # Actualizar caja
        last_cash = supabase.table("cash_operations").select("*").order("fecha", desc=True).limit(1).execute()
        new_balance = last_cash.data[0]["saldo"] + transaction["pago"]
        
        cash_op = {
            "tipo_operacion": "VENTA",
            "monto": transaction["pago"],
            "saldo": new_balance,
            "descripcion": f"Venta de prueba - {len(transaction['productos'])} productos"
        }
        supabase.table("cash_operations").insert(cash_op).execute()
        
        print(f"✅ Transacción de prueba creada: ${transaction['total']}")
        return response.data[0]
    except Exception as e:
        print(f"❌ Error al crear transacción: {e}")
        return None

def main():
    print("🌱 Insertando datos de prueba en Supabase...\n")
    
    # 1. Productos
    print("📦 Insertando productos...")
    seed_products()
    
    # 2. Saldo inicial
    print("\n💰 Configurando caja...")
    seed_cash_initial()
    
    # 3. Transacción de ejemplo
    print("\n🛒 Creando transacción de prueba...")
    seed_sample_transaction()
    
    print("\n✨ ¡Datos de prueba insertados correctamente!")
    print("\n📊 Puedes verificar en:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Supabase: https://supabase.com/dashboard")

if __name__ == "__main__":
    main()
