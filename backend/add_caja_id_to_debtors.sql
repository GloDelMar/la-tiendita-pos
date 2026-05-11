-- Agregar columna caja_id a la tabla debtors
-- Esta columna permite asociar deudores con cajas específicas

-- Agregar la columna caja_id (permitiendo NULL para deudores existentes)
ALTER TABLE debtors 
ADD COLUMN IF NOT EXISTS caja_id INTEGER;

-- Agregar foreign key constraint si la tabla cajas existe
-- Descomentar estas líneas si tienes la tabla cajas creada:
-- ALTER TABLE debtors 
-- ADD CONSTRAINT fk_debtors_caja 
-- FOREIGN KEY (caja_id) REFERENCES cajas(id) ON DELETE SET NULL;

-- Crear índice para mejorar búsquedas por caja
CREATE INDEX IF NOT EXISTS idx_debtors_caja_id ON debtors(caja_id);

-- Nota: Los deudores existentes tendrán caja_id = NULL
-- Las nuevas deudas incluirán el caja_id automáticamente
