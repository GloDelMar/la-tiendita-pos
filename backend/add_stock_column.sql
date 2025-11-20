-- ============================================
-- AGREGAR COLUMNA STOCK A LA TABLA PRODUCTS
-- ============================================

-- Agregar columna stock con valor por defecto 0
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS stock INTEGER DEFAULT 0 NOT NULL;

-- Verificar la estructura actualizada
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'products'
ORDER BY ordinal_position;
