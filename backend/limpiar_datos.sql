-- ============================================
-- ELIMINAR DATOS DE TODAS LAS CAJAS
-- (Mantiene las cajas, solo limpia sus datos)
-- ============================================

-- 1. Eliminar operaciones de caja
DELETE FROM cash_operations;

-- 2. Eliminar transacciones (recibos)
DELETE FROM transactions;

-- 3. Eliminar deudores
DELETE FROM debtors;

-- 4. Eliminar productos
DELETE FROM products;

-- 5. Verificar que todo está vacío
SELECT 
    'products' as tabla,
    COUNT(*) as total
FROM products
UNION ALL
SELECT 
    'transactions' as tabla,
    COUNT(*) as total
FROM transactions
UNION ALL
SELECT 
    'debtors' as tabla,
    COUNT(*) as total
FROM debtors
UNION ALL
SELECT 
    'cash_operations' as tabla,
    COUNT(*) as total
FROM cash_operations
UNION ALL
SELECT 
    'cajas' as tabla,
    COUNT(*) as total
FROM cajas;

-- ============================================
-- RESULTADO ESPERADO:
-- products: 0
-- transactions: 0
-- debtors: 0
-- cash_operations: 0
-- cajas: 4 (Agua, Papelería, Panadería, General)
-- ============================================
