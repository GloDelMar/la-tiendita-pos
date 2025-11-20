# 🪙 Guía para Agregar Imágenes de Monedas y Números

## 📁 Estructura de Carpetas

Las imágenes deben colocarse en las siguientes carpetas:

```
frontend/public/
├── monedas/
│   ├── 1000.png  # Billete de $1000
│   ├── 500.png   # Billete de $500
│   ├── 200.png   # Billete de $200
│   ├── 100.png   # Billete de $100
│   ├── 50.png    # Billete de $50
│   ├── 20.png    # Billete de $20
│   ├── 10.png    # Moneda de $10
│   ├── 5.png     # Moneda de $5
│   ├── 2.png     # Moneda de $2
│   ├── 1.png     # Moneda de $1
│   └── 0.5.png   # Moneda de $0.50
│
└── numeros/
    ├── 0.png     # Número 0
    ├── 1.png     # Número 1
    ├── 2.png     # Número 2
    ├── 3.png     # Número 3
    ├── 4.png     # Número 4
    ├── 5.png     # Número 5
    ├── 6.png     # Número 6
    ├── 7.png     # Número 7
    ├── 8.png     # Número 8
    └── 9.png     # Número 9
```

## 🎨 Especificaciones de las Imágenes

### Monedas y Billetes
- **Formato:** PNG con fondo transparente
- **Tamaño recomendado:** 300x150px para billetes, 150x150px para monedas
- **Resolución:** 72-150 DPI
- **Peso:** Máximo 200KB por imagen

### Números
- **Formato:** PNG con fondo transparente
- **Tamaño recomendado:** 200x200px
- **Colores:** Brillantes y de alto contraste
- **Peso:** Máximo 100KB por imagen

## 📋 Cómo Copiar las Imágenes

### Desde el proyecto original de Kivy:

```bash
# Copiar monedas
cp -r /ruta/al/proyecto/kivy/assets/monedas/* /home/glo_suarez/la_tiendita/frontend/public/monedas/

# Copiar números
cp -r /ruta/al/proyecto/kivy/assets/numeros/* /home/glo_suarez/la_tiendita/frontend/public/numeros/
```

### Verificar que las imágenes se copiaron:

```bash
ls -la /home/glo_suarez/la_tiendita/frontend/public/monedas/
ls -la /home/glo_suarez/la_tiendita/frontend/public/numeros/
```

## 🔄 Fallback Automático

Si las imágenes no están disponibles, el sistema mostrará automáticamente:
- **Monedas/Billetes:** Emojis 💵 y 🪙
- **Números:** Números en texto grande y colorido

## ✅ Características Implementadas

### 1. Selector Visual de Monedas (`/monedas`)
- ✅ Muestra todas las denominaciones mexicanas
- ✅ Imágenes reales de billetes y monedas
- ✅ Botones grandes +/- para seleccionar cantidades
- ✅ Cálculo automático del total
- ✅ Cálculo del cambio
- ✅ Sugerencia de cómo dar el cambio óptimo

### 2. Selector de Cantidad con Números
- ✅ Teclado numérico visual con imágenes
- ✅ Botones grandes de 0-9
- ✅ Botón de borrar (⌫)
- ✅ Botón de limpiar (🗑️)
- ✅ Display grande mostrando la cantidad

### 3. Integración en Ventas
- ✅ Al hacer clic en un producto, abre modal de cantidad
- ✅ Al hacer clic en "¿Con cuánto pagas?", abre selector de monedas
- ✅ Todo completamente visual y accesible

## 🎯 Beneficios para Niños con Discapacidad

1. **No necesitan saber contar:** Las imágenes representan cantidades reales
2. **No necesitan sumar:** El sistema calcula automáticamente
3. **No necesitan restar:** El sistema muestra el cambio y cómo formarlo
4. **Todo es visual:** Colores, imágenes grandes, botones táctiles
5. **Retroalimentación inmediata:** Ven los resultados en tiempo real

## 🚀 Próximos Pasos

1. Copiar las imágenes a las carpetas correspondientes
2. Reiniciar el servidor de Next.js si está corriendo
3. Probar el sistema en http://localhost:3000/ventas
4. Hacer una venta y probar el selector de monedas

## ❓ Si no tienes las imágenes

Puedes descargar imágenes de:
- **Banco de México:** Sitio oficial con imágenes de billetes y monedas
- **Flaticon:** Iconos de números coloridos
- **O usar las actuales emojis** que ya funcionan como fallback
