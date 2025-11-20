# Guía de Configuración de Supabase

## Paso 1: Crear Proyecto en Supabase

1. Ve a [https://supabase.com](https://supabase.com)
2. Inicia sesión o crea una cuenta gratuita
3. Click en "New Project"
4. Completa los datos:
   - **Name**: `la-tiendita-pos`
   - **Database Password**: (genera una contraseña segura y guárdala)
   - **Region**: Elige la más cercana (por ejemplo: South America - São Paulo)
   - **Pricing Plan**: Free
5. Click en "Create new project" (tomará 1-2 minutos)

## Paso 2: Obtener Credenciales

Una vez creado el proyecto:

1. Ve a **Settings** (⚙️) > **API**
2. Copia estas 2 credenciales:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. Crea el archivo `.env` en la carpeta `/backend`:

```bash
# En la terminal, dentro del proyecto:
cd /home/glo_suarez/la_tiendita/backend
touch .env
```

4. Edita el archivo `.env` con tus credenciales:

```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Paso 3: Crear Tablas en la Base de Datos

1. En Supabase, ve a **SQL Editor** (icono </> en el menú lateral)
2. Click en "New query"
3. Copia y pega el contenido del archivo `database_schema.sql`
4. Click en "Run" (▶️)
5. Deberías ver: "Success. No rows returned"

**Verifica las tablas creadas:**
- Ve a **Table Editor** (icono 📊)
- Deberías ver: `products`, `transactions`, `debtors`, `cash_operations`

## Paso 4: Configurar Storage para Imágenes

1. Ve a **Storage** (icono 📦 en el menú lateral)
2. Click en "Create a new bucket"
3. Configura:
   - **Name**: `product-images`
   - **Public bucket**: ✅ (activar)
   - **File size limit**: 5 MB
   - **Allowed MIME types**: `image/png, image/jpeg, image/webp, image/gif`
4. Click en "Create bucket"

**Configurar políticas de acceso:**

1. Dentro del bucket `product-images`, click en "Policies"
2. Click en "New Policy" > "For full customization"
3. Crea la política de lectura:
   - **Policy name**: `Public Access`
   - **Policy definition**: SELECT
   - **Target roles**: `public`
   - Habilita: ✅ SELECT
   - Click en "Review" > "Save policy"

4. Crea otra política para escritura:
   - **Policy name**: `Allow Authenticated Upload`
   - **Policy definition**: INSERT
   - **Target roles**: `anon` (para permitir subidas desde el backend)
   - Habilita: ✅ INSERT
   - Click en "Review" > "Save policy"

5. Crea política para borrado:
   - **Policy name**: `Allow Authenticated Delete`
   - **Policy definition**: DELETE
   - **Target roles**: `anon`
   - Habilita: ✅ DELETE
   - Click en "Review" > "Save policy"

## Paso 5: Verificar Conexión

1. Instala las dependencias del backend:

```bash
cd /home/glo_suarez/la_tiendita/backend
python -m venv venv
source venv/bin/activate  # En Linux/Mac
pip install -r requirements.txt
```

2. Inicia el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

3. Abre el navegador en: [http://localhost:8000/docs](http://localhost:8000/docs)
4. Prueba el endpoint de salud: `GET /health`
5. Deberías ver: `{"status": "healthy"}`

## Paso 6: Probar Endpoints

### Crear un producto:

En Swagger UI (`/docs`):

1. Expand `POST /api/products`
2. Click en "Try it out"
3. Ingresa:
```json
{
  "name": "Coca Cola 600ml",
  "price": 1.50
}
```
4. Click en "Execute"
5. Deberías ver respuesta 201 con el producto creado

### Ver productos:

1. Expand `GET /api/products`
2. Click en "Try it out" > "Execute"
3. Deberías ver el array con tu producto

## Paso 7: Insertar Datos de Prueba (Opcional)

Si quieres datos de ejemplo:

```sql
-- Productos de ejemplo
INSERT INTO products (name, price) VALUES
('Coca Cola 600ml', 1.50),
('Pepsi 600ml', 1.50),
('Agua 500ml', 0.75),
('Galletas Oreo', 2.00),
('Pan Blanco', 1.20),
('Leche 1L', 1.80),
('Café Nescafé 100g', 5.50),
('Azúcar 1kg', 2.30),
('Arroz 1kg', 1.90),
('Aceite 900ml', 3.50);

-- Inicializar saldo de caja
INSERT INTO cash_operations (tipo_operacion, monto, saldo, descripcion)
VALUES ('AJUSTE', 100.00, 100.00, 'Saldo inicial de caja');
```

## 🎉 ¡Configuración Completada!

Tu backend ahora está conectado a Supabase y listo para usar.

### Próximos pasos:
- ✅ Base de datos configurada
- ✅ Storage configurado
- ⏳ Crear frontend Next.js
- ⏳ Conectar frontend con backend
- ⏳ Deploy a producción

## Solución de Problemas

### Error de conexión:
- Verifica que el archivo `.env` tiene las credenciales correctas
- Asegúrate de que `SUPABASE_URL` y `SUPABASE_KEY` están sin comillas adicionales

### Error 403 en Storage:
- Verifica que el bucket es público
- Revisa que las políticas de acceso están configuradas

### Tablas no se crean:
- Asegúrate de copiar TODO el contenido de `database_schema.sql`
- Ejecuta el SQL por bloques si hay errores (primero las tablas, luego índices, luego funciones)
