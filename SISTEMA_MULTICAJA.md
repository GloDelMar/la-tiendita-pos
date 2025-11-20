# 📦 Sistema Multi-Caja - La Tiendita

## 🎯 Descripción

Sistema que permite gestionar múltiples cajas independientes, cada una con su propio inventario de productos y contabilidad separada.

## ✨ Características

- **Cajas Independientes**: Agua, Papelería, Panadería, General (y las que quieras agregar)
- **Inventarios Separados**: Cada caja tiene sus propios productos
- **Contabilidad Independiente**: Cada caja maneja su propio saldo y operaciones
- **Transacciones por Caja**: Las ventas se registran en la caja correspondiente

## 🚀 Instalación

### 1. Ejecutar Migración en Supabase

1. Ve a tu proyecto en Supabase (https://supabase.com)
2. Abre el **SQL Editor**
3. Copia y pega el contenido de `backend/migration_multi_caja.sql`
4. Ejecuta el script

Esto creará:
- ✅ Tabla `cajas` con 4 cajas predeterminadas
- ✅ Columna `caja_id` en tablas `products`, `transactions`, `cash_operations`
- ✅ Funciones actualizadas para manejar cajas
- ✅ Vistas para dashboard por caja

### 2. Verificar Migración

```sql
-- Ver cajas creadas
SELECT * FROM cajas;

-- Ver productos con su caja asignada
SELECT id, name, caja_id FROM products LIMIT 10;

-- Ver saldo por caja
SELECT * FROM dashboard_summary_por_caja;
```

### 3. Reiniciar Servidores

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

## 📝 Cambios Implementados

### Backend

#### Nuevo: `models/schemas.py`
- ✅ Modelos `Caja`, `CajaCreate`, `CajaUpdate`
- ✅ Campo `caja_id` agregado a `Product`, `Transaction`, `CashOperation`

#### Nuevo: `routers/cajas.py`
Endpoints:
- `GET /api/cajas` - Listar todas las cajas
- `GET /api/cajas/{id}` - Obtener caja específica
- `POST /api/cajas` - Crear nueva caja
- `PATCH /api/cajas/{id}` - Actualizar caja
- `DELETE /api/cajas/{id}` - Desactivar caja (soft delete)
- `GET /api/cajas/{id}/saldo` - Obtener saldo de una caja
- `GET /api/cajas/{id}/productos` - Obtener productos de una caja

#### Actualizado: `routers/products.py`
- ✅ `GET /api/products?caja_id={id}` - Filtrar productos por caja

#### Actualizado: `routers/cash.py`
- ✅ `GET /api/cash?caja_id={id}` - Filtrar operaciones por caja
- ✅ `GET /api/cash/balance?caja_id={id}` - Obtener saldo de caja específica
- ✅ Operaciones de caja ahora calculan saldo por caja individual

### Frontend

#### Nuevo: `lib/api.ts`
```typescript
// API para cajas
export const cajasApi = {
  getAll(activaOnly?: boolean)
  getById(id: number)
  create(caja: {...})
  update(id: number, caja: {...})
  delete(id: number)
  getSaldo(id: number)
  getProductos(id: number)
}

// Actualizado: productos con filtro de caja
productsApi.getAll(cajaId?: number)
```

## 💡 Uso del Sistema

### Crear una Nueva Caja

```typescript
await cajasApi.create({
  nombre: "Dulcería",
  descripcion: "Caja para venta de dulces y chocolates",
  activa: true,
  saldo_inicial: 500
});
```

### Agregar Productos a una Caja

```typescript
await productsApi.create({
  name: "Botella de Agua 1L",
  price: 15,
  stock: 50,
  caja_id: 1  // ID de la caja "Agua"
});
```

### Obtener Productos de una Caja

```typescript
// Solo productos de la caja "Papelería" (ID: 2)
const productosPapeleria = await productsApi.getAll(2);
```

### Registrar Venta en una Caja

```typescript
await transactionsApi.create({
  cliente: "Juan Pérez",
  grupo: "3° Secundaria",
  productos: [...],
  total: 45,
  pago: 50,
  cambio: 5,
  pagado: "SI",
  caja_id: 1  // Venta en caja "Agua"
});
```

### Ver Saldo de una Caja

```typescript
const saldo = await cajasApi.getSaldo(1);
// { caja_id: 1, caja_nombre: "Agua", saldo: 1250.50 }
```

## 🏗️ Estructura de Datos

### Tabla: cajas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único |
| nombre | VARCHAR(200) | Nombre de la caja (único) |
| descripcion | TEXT | Descripción opcional |
| activa | BOOLEAN | Si está activa o no |
| saldo_inicial | DECIMAL(10,2) | Saldo inicial al crear la caja |
| created_at | TIMESTAMPTZ | Fecha de creación |

### Cajas Predeterminadas

1. **Agua** - Bebidas y agua
2. **Papelería** - Artículos escolares
3. **Panadería** - Pan y productos de panadería
4. **General** - Otros productos

## 🔄 Migración de Datos Existentes

Todos los productos, transacciones y operaciones existentes se asignaron automáticamente a la caja "General" durante la migración.

Para reasignar productos a otras cajas:

```typescript
await productsApi.update(productId, {
  caja_id: 2  // Mover a caja "Papelería"
});
```

## 📊 Reportes por Caja

### Dashboard por Caja (SQL)

```sql
SELECT * FROM dashboard_summary_por_caja;
```

Retorna para cada caja activa:
- Total de productos
- Saldo actual
- Ventas del día
- Total de ventas del día

### Dashboard Consolidado

```sql
SELECT * FROM dashboard_summary;
```

Retorna totales de todas las cajas combinadas.

## 🎨 Próximos Pasos para el Frontend

Ahora que el backend está listo, puedes implementar en el frontend:

1. **Página de Gestión de Cajas** (`/cajas`)
   - Listar todas las cajas
   - Crear/editar/desactivar cajas
   - Ver saldo y estadísticas por caja

2. **Selector de Caja en Ventas**
   - Dropdown para seleccionar caja activa
   - Filtrar productos por caja seleccionada
   - Registrar venta en la caja correcta

3. **Dashboard con Tabs por Caja**
   - Vista general (todas las cajas)
   - Tab para cada caja individual
   - Gráficas de ventas por caja

4. **Filtros por Caja**
   - En página de productos
   - En historial de transacciones
   - En operaciones de caja

## ⚠️ Notas Importantes

- Las cajas desactivadas no se pueden eliminar físicamente (soft delete)
- Cada caja mantiene su saldo independiente
- Las transacciones deben indicar a qué caja pertenecen
- Si no se especifica caja_id, se comporta como sistema legacy (todas las cajas)

## 🐛 Troubleshooting

### Error: "La caja no existe"
Verifica que el ID de caja existe: `SELECT * FROM cajas WHERE id = X;`

### Saldo incorrecto
Ejecuta: `SELECT get_caja_balance(caja_id);`

### Productos sin caja
Los productos legacy tienen `caja_id = NULL`. Asígnalos:
```sql
UPDATE products SET caja_id = X WHERE caja_id IS NULL;
```

## 📞 Soporte

Si encuentras problemas, revisa:
1. Logs del backend para errores de SQL
2. Que la migración se ejecutó completamente
3. Que los IDs de caja existen antes de usarlos
