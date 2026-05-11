#!/usr/bin/env python3
"""
Script para preparar datos base del sistema multi-caja en MongoDB.
"""
from database import db, get_next_sequence
from datetime import datetime
from pymongo import ASCENDING


def ensure_indexes():
    db.cajas.create_index([("id", ASCENDING)], unique=True)
    db.cajas.create_index([("nombre", ASCENDING)], unique=True)


def seed_default_cajas():
    cajas_default = [
        {"nombre": "Agua", "descripcion": "Caja para venta de agua y bebidas", "saldo_inicial": 0},
        {"nombre": "Papelería", "descripcion": "Caja para venta de artículos de papelería", "saldo_inicial": 0},
        {"nombre": "Panadería", "descripcion": "Caja para venta de pan y productos de panadería", "saldo_inicial": 0},
        {"nombre": "General", "descripcion": "Caja general para otros productos", "saldo_inicial": 0},
    ]

    for caja_data in cajas_default:
        existing = db.cajas.find_one({"nombre": caja_data["nombre"]}, {"_id": 0, "id": 1})
        if existing:
            print(f"   ℹ️  Caja '{caja_data['nombre']}' ya existe")
            continue

        caja_doc = {
            "id": get_next_sequence("cajas"),
            "nombre": caja_data["nombre"],
            "descripcion": caja_data["descripcion"],
            "saldo_inicial": float(caja_data["saldo_inicial"]),
            "activa": True,
            "created_at": datetime.utcnow(),
        }
        db.cajas.insert_one(caja_doc)
        print(f"   ✅ Caja '{caja_data['nombre']}' creada")


def main():
    print("🚀 Inicializando estructura base multi-caja en MongoDB...")
    print("=" * 60)
    print()

    print("📦 Paso 1: Verificando índices...")
    ensure_indexes()
    print("   ✅ Índices verificados")
    print()

    print("📝 Paso 2: Insertando cajas predeterminadas...")
    seed_default_cajas()
    print()

    print("✅ Verificando cajas creadas:")
    cajas = list(db.cajas.find({}, {"_id": 0, "id": 1, "nombre": 1, "activa": 1, "saldo_inicial": 1}).sort("nombre", ASCENDING))
    if cajas:
        print()
        for caja in cajas:
            status = "✓ Activa" if caja.get("activa") else "✗ Inactiva"
            print(f"   📦 {caja['nombre']} (ID: {caja['id']}) - {status}")
            print(f"      Saldo inicial: ${float(caja.get('saldo_inicial', 0)):.2f}")
        print()
        print(f"✨ Total: {len(cajas)} cajas encontradas")
    else:
        print("   ⚠️  No se encontraron cajas")

    print()
    print("=" * 60)
    print("🎉 ¡Inicialización completada!")
    print()


if __name__ == "__main__":
    main()
