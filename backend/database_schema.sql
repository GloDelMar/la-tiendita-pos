-- Tabla de Productos
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para productos
CREATE INDEX idx_products_name ON products(name);

-- Tabla de Transacciones
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    cliente VARCHAR(200) NOT NULL DEFAULT 'Cliente',
    grupo VARCHAR(200) NOT NULL DEFAULT 'General',
    productos JSONB NOT NULL,
    total DECIMAL(10, 2) NOT NULL CHECK (total > 0),
    pago DECIMAL(10, 2) NOT NULL CHECK (pago >= 0),
    cambio DECIMAL(10, 2) NOT NULL CHECK (cambio >= 0),
    pagado VARCHAR(2) NOT NULL CHECK (pagado IN ('SI', 'NO')),
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para transacciones
CREATE INDEX idx_transactions_fecha ON transactions(fecha DESC);
CREATE INDEX idx_transactions_cliente ON transactions(cliente);
CREATE INDEX idx_transactions_grupo ON transactions(grupo);
CREATE INDEX idx_transactions_pagado ON transactions(pagado);

-- Tabla de Deudores
CREATE TABLE debtors (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    grupo VARCHAR(200) NOT NULL,
    deuda DECIMAL(10, 2) NOT NULL CHECK (deuda > 0),
    fecha_primera_deuda TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ultima_compra TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(nombre, grupo)
);

-- Índices para deudores
CREATE INDEX idx_debtors_nombre ON debtors(nombre);
CREATE INDEX idx_debtors_grupo ON debtors(grupo);
CREATE INDEX idx_debtors_deuda ON debtors(deuda DESC);

-- Tabla de Operaciones de Caja
CREATE TABLE cash_operations (
    id BIGSERIAL PRIMARY KEY,
    tipo_operacion VARCHAR(20) NOT NULL CHECK (tipo_operacion IN ('VENTA', 'INGRESO', 'EGRESO', 'AJUSTE')),
    monto DECIMAL(10, 2) NOT NULL CHECK (monto != 0),
    saldo DECIMAL(10, 2) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para operaciones de caja
CREATE INDEX idx_cash_operations_fecha ON cash_operations(fecha DESC);
CREATE INDEX idx_cash_operations_tipo ON cash_operations(tipo_operacion);

-- Row Level Security (RLS) - Activar según necesidad
-- ALTER TABLE products ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE debtors ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cash_operations ENABLE ROW LEVEL SECURITY;

-- Políticas de acceso (ejemplo para autenticación futura)
-- CREATE POLICY "Allow public read access" ON products FOR SELECT USING (true);
-- CREATE POLICY "Allow authenticated insert" ON products FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Storage bucket para imágenes de productos
-- Ejecutar en el dashboard de Supabase > Storage
-- 1. Crear bucket: "product-images"
-- 2. Hacer público el bucket
-- 3. Configurar políticas de acceso

-- Funciones útiles
CREATE OR REPLACE FUNCTION get_daily_sales(date_param DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    total_ventas DECIMAL,
    total_transacciones BIGINT,
    total_efectivo DECIMAL,
    total_credito DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(total), 0)::DECIMAL as total_ventas,
        COUNT(*)::BIGINT as total_transacciones,
        COALESCE(SUM(pago), 0)::DECIMAL as total_efectivo,
        COALESCE(SUM(CASE WHEN pagado = 'NO' THEN total - pago ELSE 0 END), 0)::DECIMAL as total_credito
    FROM transactions
    WHERE DATE(fecha) = date_param;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener productos más vendidos
CREATE OR REPLACE FUNCTION get_top_products(days_back INT DEFAULT 30, limit_count INT DEFAULT 10)
RETURNS TABLE (
    product_name TEXT,
    total_quantity BIGINT,
    total_sales DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (producto->>'nombre')::TEXT as product_name,
        SUM((producto->>'cantidad')::INT)::BIGINT as total_quantity,
        SUM((producto->>'subtotal')::DECIMAL)::DECIMAL as total_sales
    FROM transactions,
    LATERAL jsonb_array_elements(productos) as producto
    WHERE fecha >= NOW() - (days_back || ' days')::INTERVAL
    GROUP BY producto->>'nombre'
    ORDER BY total_sales DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Vista para dashboard
CREATE OR REPLACE VIEW dashboard_summary AS
SELECT 
    (SELECT COUNT(*) FROM products) as total_productos,
    (SELECT COUNT(*) FROM debtors) as total_deudores,
    (SELECT COALESCE(SUM(deuda), 0) FROM debtors) as total_deuda,
    (SELECT saldo FROM cash_operations ORDER BY fecha DESC LIMIT 1) as saldo_caja,
    (SELECT COUNT(*) FROM transactions WHERE DATE(fecha) = CURRENT_DATE) as ventas_hoy,
    (SELECT COALESCE(SUM(total), 0) FROM transactions WHERE DATE(fecha) = CURRENT_DATE) as total_ventas_hoy;
