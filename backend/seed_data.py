"""
Script para insertar datos de prueba en MongoDB
Ejecutar: python seed_data.py
"""
import sys
from pathlib import Path
from datetime import datetime
from pymongo import DESCENDING

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import db, get_next_sequence

def seed_products():
    """Insertar productos de prueba"""
    try:
        now = datetime.utcnow()
        raw_products = [
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

        products = []
        for p in raw_products:
            p_doc = {
                "id": get_next_sequence("products"),
                "name": p["name"],
                "price": p["price"],
                "stock": 0,
                "image_url": None,
                "caja_id": None,
                "created_at": now,
            }
            products.append(p_doc)

        db.products.insert_many(products)
        print(f"✅ {len(products)} productos insertados correctamente")
        return products
    except Exception as e:
        print(f"❌ Error al insertar productos: {e}")
        return None

def seed_cash_initial():
    """Insertar saldo inicial de caja"""
    try:
        # Verificar si ya existe un saldo
        existing = db.cash_operations.find_one({}, {"_id": 0})
        if existing:
            print("ℹ️  Ya existe un saldo de caja, omitiendo inserción")
            return existing

        # Crear saldo inicial
        initial_cash = {
            "id": get_next_sequence("cash_operations"),
            "tipo_operacion": "AJUSTE",
            "monto": 100.00,
            "saldo": 100.00,
            "descripcion": "Saldo inicial de caja",
            "caja_id": None,
            "fecha": datetime.utcnow(),
        }
        db.cash_operations.insert_one(initial_cash)
        print(f"✅ Saldo inicial de caja: ${initial_cash['saldo']}")
        return initial_cash
    except Exception as e:
        print(f"❌ Error al insertar saldo inicial: {e}")
        return None

def seed_sample_transaction():
    """Crear una transacción de ejemplo"""
    try:
        # Obtener algunos productos
        products = list(db.products.find({}, {"_id": 0}).limit(3))
        if not products:
            print("⚠️  No hay productos, primero ejecuta seed_products()")
            return None

        # Crear transacción
        now = datetime.utcnow()
        transaction = {
            "id": get_next_sequence("transactions"),
            "cliente": "Cliente de Prueba",
            "grupo": "General",
            "productos": [
                {
                    "nombre": products[0]["name"],
                    "cantidad": 2,
                    "precio_unitario": products[0]["price"],
                    "subtotal": products[0]["price"] * 2
                },
                {
                    "nombre": products[1]["name"],
                    "cantidad": 1,
                    "precio_unitario": products[1]["price"],
                    "subtotal": products[1]["price"]
                }
            ],
            "total": (products[0]["price"] * 2) + products[1]["price"],
            "pago": (products[0]["price"] * 2) + products[1]["price"],
            "cambio": 0,
            "pagado": "SI",
            "caja_id": None,
            "fecha": now,
        }

        db.transactions.insert_one(transaction)

        # Actualizar caja
        last_cash = db.cash_operations.find_one({}, {"_id": 0}, sort=[("fecha", DESCENDING), ("id", DESCENDING)])
        current_balance = float(last_cash["saldo"]) if last_cash else 0.0
        new_balance = current_balance + transaction["pago"]

        cash_op = {
            "id": get_next_sequence("cash_operations"),
            "tipo_operacion": "VENTA",
            "monto": transaction["pago"],
            "saldo": new_balance,
            "descripcion": f"Venta de prueba - {len(transaction['productos'])} productos",
            "caja_id": None,
            "fecha": now,
        }
        db.cash_operations.insert_one(cash_op)

        print(f"✅ Transacción de prueba creada: ${transaction['total']}")
        return transaction
    except Exception as e:
        print(f"❌ Error al crear transacción: {e}")
        return None

def main():
    print("🌱 Insertando datos de prueba en MongoDB...\n")
    
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
    print("   - MongoDB: revisa la base configurada en MONGODB_DB")

if __name__ == "__main__":
    main()
