# La Tiendita POS - Sistema Web

Sistema de Punto de Venta moderno desarrollado con Next.js, FastAPI y Supabase.

## 🏗️ Arquitectura

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Base de Datos**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage (imágenes de productos)

## 📁 Estructura del Proyecto

```
la_tiendita/
├── frontend/          # Aplicación Next.js
├── backend/           # API FastAPI
│   ├── routers/      # Endpoints de la API
│   ├── models/       # Modelos Pydantic
│   ├── database.py   # Cliente Supabase
│   ├── main.py       # App FastAPI
│   └── .env          # Variables de entorno
├── kivy_app/         # App original de Kivy (referencia)
└── README.md
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Node.js 20+ (recomendado)
- Cuenta de Supabase (gratuita)

### Configuración Backend

1. **Crear entorno virtual**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
```bash
# Editar backend/.env con tus credenciales de Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui
# Opcional (compatibilidad):
SUPABASE_KEY=tu_api_key_aqui
```

4. **Crear base de datos**:
   - Ve a tu proyecto de Supabase
   - SQL Editor > New Query
   - Pega el contenido de `backend/database_schema.sql`
   - Ejecuta (Run)

5. **Configurar Storage**:
   - Storage > Create bucket: `product-images` (público)
   - Configura las políticas según `SUPABASE_SETUP.md`

6. **Insertar datos de prueba** (opcional):
```bash
python seed_data.py
```

7. **Iniciar servidor**:
```bash
uvicorn main:app --reload
```

API disponible en: http://localhost:8000
Documentación: http://localhost:8000/docs

### Configuración Frontend

1. **Instalar dependencias**:
```bash
cd frontend
npm install
```

2. **Configurar variables de entorno**:
```bash
# Crear frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_PASSWORD=cicloescolar2025-2026
```

> **Nota de Seguridad**: La contraseña por defecto es `cicloescolar2025-2026`. Asegúrate de cambiarla en producción.

3. **Iniciar aplicación**:
```bash
npm run dev
```

Aplicación disponible en: http://localhost:3000

## 🔐 Sistema de Autenticación

El sistema cuenta con protección por contraseña:

- **Acceso**: Solo personal autorizado del Taller de Formación Laboral, CAM15-Nayarit
- **Contraseña por defecto**: `cicloescolar2025-2026`
- **Configuración**: Se define en `NEXT_PUBLIC_AUTH_PASSWORD` del archivo `.env.local`
- **Protección**: Todas las páginas excepto `/login` requieren autenticación
- **Sesión**: Se mantiene en localStorage del navegador
- **Cerrar sesión**: Botón "Salir" en la navegación superior

Para cambiar la contraseña, modifica el valor en el archivo `.env.local`

## 📚 API Endpoints

### Productos (`/api/products`)
- `GET /` - Listar todos los productos
- `GET /{id}` - Obtener producto por ID
- `POST /` - Crear producto
- `PUT /{id}` - Actualizar producto
- `DELETE /{id}` - Eliminar producto
- `POST /upload-image/{id}` - Subir imagen

### Transacciones (`/api/transactions`)
- `GET /` - Listar transacciones (con filtros)
- `GET /{id}` - Obtener transacción por ID
- `POST /` - Crear transacción
- `GET /stats/daily` - Estadísticas del día
- `GET /stats/monthly` - Estadísticas del mes

### Deudores (`/api/debtors`)
- `GET /` - Listar deudores
- `GET /{id}` - Obtener deudor por ID
- `GET /by-name/{nombre}/{grupo}` - Buscar por nombre
- `POST /` - Crear deudor
- `PATCH /{id}/pay` - Registrar pago
- `PUT /{id}` - Actualizar deuda
- `DELETE /{id}` - Eliminar deudor
- `GET /stats/summary` - Resumen de deudas

### Caja (`/api/cash`)
- `GET /` - Listar operaciones
- `GET /balance` - Saldo actual
- `POST /income` - Registrar ingreso
- `POST /expense` - Registrar egreso
- `POST /adjust` - Ajustar saldo
- `GET /stats/daily` - Estadísticas del día

Ver documentación completa en: `backend/API_DOCS.md`

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend (Render)
1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Deploy automático desde `main`

### Frontend (Vercel)
1. Conectar repositorio a Vercel
2. Configurar variables de entorno
3. Deploy automático desde `main`

Ver guías detalladas en la carpeta `/docs`

## 🛠️ Tecnologías

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (data fetching)
- Zustand (state management)

### Backend
- FastAPI 0.115.5
- Pydantic 2.10.3 (validación)
- Supabase 2.10.0 (database + storage)
- Python-dotenv (env vars)
- ReportLab (generación de PDFs)

### Base de Datos
- PostgreSQL (Supabase)
- 4 tablas: products, transactions, debtors, cash_operations
- Storage bucket para imágenes

## 📝 Características

✅ **Gestión de Productos**
- CRUD completo
- Carga de imágenes
- Precios y stock

✅ **Punto de Venta**
- Carrito de compras
- Cálculo automático de totales
- Registro de transacciones

✅ **Gestión de Créditos**
- Registro de deudores
- Pagos parciales/totales
- Historial de deudas

✅ **Control de Caja**
- Saldo en tiempo real
- Ingresos y egresos
- Estadísticas diarias/mensuales

✅ **Reportes y Estadísticas**
- Ventas diarias/mensuales
- Productos más vendidos
- Dashboard con métricas

## 🔒 Seguridad

- API Keys en variables de entorno
- CORS configurado
- Validación de datos con Pydantic
- Storage con políticas de acceso

## 📄 Licencia

MIT

## 👥 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📞 Soporte

- Documentación: `/docs`
- Issues: GitHub Issues
- Email: soporte@latiendita.com

---

Desarrollado con ❤️ para facilitar la gestión de pequeños negocios
