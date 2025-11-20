#!/usr/bin/env python3
"""
Script para ejecutar la migración del sistema multi-caja en Supabase
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("🚀 Iniciando migración del sistema multi-caja...")
print("=" * 60)
print()

# Paso 1: Crear tabla de cajas
print("📦 Paso 1: Creando tabla de cajas...")
try:
    # Verificar si la tabla ya existe consultándola
    result = supabase.table('cajas').select('id').limit(1).execute()
    print("   ✅ La tabla 'cajas' ya existe")
except Exception as e:
    print(f"   ℹ️  La tabla 'cajas' no existe, necesita ser creada manualmente")
    print()
    print("⚠️  IMPORTANTE: Supabase no permite crear tablas via Python client.")
    print("   Debes ejecutar el SQL manualmente en Supabase SQL Editor:")
    print()
    print("   1. Ve a: https://supabase.com/dashboard/project/imphmumiaqnedeqfeaeh")
    print("   2. Abre 'SQL Editor' en el menú lateral")
    print("   3. Crea una nueva query")
    print("   4. Copia y pega el contenido completo de:")
    print("      /home/glo_suarez/la_tiendita/backend/migration_multi_caja.sql")
    print("   5. Haz clic en 'RUN' o presiona Ctrl+Enter")
    print()
    print("   El script SQL está diseñado para ser seguro (usa IF NOT EXISTS)")
    print("   y se puede ejecutar múltiples veces sin problemas.")
    print()
    exit(1)

print()

# Paso 2: Insertar cajas predeterminadas
print("📝 Paso 2: Insertando cajas predeterminadas...")
cajas_default = [
    {"nombre": "Agua", "descripcion": "Caja para venta de agua y bebidas", "saldo_inicial": 0},
    {"nombre": "Papelería", "descripcion": "Caja para venta de artículos de papelería", "saldo_inicial": 0},
    {"nombre": "Panadería", "descripcion": "Caja para venta de pan y productos de panadería", "saldo_inicial": 0},
    {"nombre": "General", "descripcion": "Caja general para otros productos", "saldo_inicial": 0},
]

for caja_data in cajas_default:
    try:
        # Verificar si ya existe
        check = supabase.table('cajas').select('id').eq('nombre', caja_data['nombre']).execute()
        if check.data:
            print(f"   ℹ️  Caja '{caja_data['nombre']}' ya existe")
        else:
            # Insertar
            result = supabase.table('cajas').insert(caja_data).execute()
            print(f"   ✅ Caja '{caja_data['nombre']}' creada")
    except Exception as e:
        print(f"   ⚠️  Error con caja '{caja_data['nombre']}': {e}")

print()

# Paso 3: Verificar columnas caja_id en otras tablas
print("🔍 Paso 3: Verificando estructura de tablas...")
print("   ⚠️  Las columnas 'caja_id' deben agregarse manualmente via SQL Editor")
print("   (Incluidas en migration_multi_caja.sql)")

print()

# Paso 4: Verificar que las cajas se crearon
print("✅ Verificando cajas creadas:")
try:
    result = supabase.table('cajas').select('id, nombre, activa, saldo_inicial').order('nombre').execute()
    if result.data:
        print()
        for caja in result.data:
            status = "✓ Activa" if caja['activa'] else "✗ Inactiva"
            print(f"   📦 {caja['nombre']} (ID: {caja['id']}) - {status}")
            print(f"      Saldo inicial: ${caja['saldo_inicial']:.2f}")
        print()
        print(f"✨ Total: {len(result.data)} cajas encontradas")
    else:
        print("   ⚠️  No se encontraron cajas")
except Exception as e:
    print(f"   ❌ Error verificando cajas: {e}")

print()
print("=" * 60)
print("🎉 ¡Migración base completada!")
print()
print("📋 NOTA IMPORTANTE:")
print("   Para completar la migración, debes ejecutar el SQL completo")
print("   en Supabase SQL Editor para agregar las columnas caja_id")
print("   a las tablas products, transactions y cash_operations.")
print()
