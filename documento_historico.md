# Documento Histórico de Construcción de Datos Sintéticos - Tu Buñuelito

Este documento describe la metodología, supuestos y parámetros utilizados para la generación de la data sintética de ventas de la PYME "Tu Buñuelito".

## 1. Información General
- **Rango de Tiempo**: 1 de enero de 2017 hasta marzo de 2026 (Actualización continua).
- **Frecuencia**: Diaria para operaciones; Mensual y Anual para indicadores macroeconómicos.
- **Unidad de Medida**: Unidades de buñuelos, libras (materia prima) y kits (materia prima cuantificada en unidades).

## 2. Reglas de Validación y Consistencia (Auditoría de Datos)
Para asegurar que la data sea 100% coherente para modelos de Machine Learning, hemos implementado y validado las siguientes reglas:

### 2.1. Reglas de Promoción (Estrategia 2x1)
Cuando el campo `es_promocion` es igual a 1 (Activo):
1. **Paridad Exacta**: `unidades_pagas` debe ser exactamente igual a `unidades_bonificadas`.
2. **Número Par**: La suma (`unidades_totales`) debe ser siempre un número par para soportar la paridad 1:1.
3. **Consistencia en Inventario**: En el archivo de inventario, las `ventas_reales_bonificadas` deben ser iguales a las `ventas_reales_pagas`. Si hay insuficiente stock preparado, la reducción del bono debe ser proporcional a la venta real pagada.

### 2.2. Reglas de la Demanda (Integridad)
1. **Identidad Fundamental**: `unidades_totales = unidades_pagas + unidades_bonificadas`.
2. **Cruce de Archivos**: `unidades_totales (ventas)` debe coincidir al 100% con `demanda_teorica_total (inventario)`.
3. **Reconstrucción de Demanda**: `demanda_teorica_total = ventas_reales_totales + unidades_agotadas`. Esta fórmula permite medir exactamente la "venta pérdida" por mala gestión de stock.

### 2.3. Reglas de Inventario y Bodega
1. **Continuidad Física**: El `kit_inicial_bodega` del día T debe ser igual al `kit_final_bodega` del día T-1. No puede haber saltos de masa sin un registro en `kit_recibido`.
2. **Gasto de Materia Prima**: Solo se descuenta de la bodega lo que fue **preparado** (frito). Los buñuelos que terminan como desperdicio ya salieron de la bodega en forma de harina al inicio del día.
3. **Relación Técnica**: `1 libra = 50 buñuelos (kits)`.

## 3. Lógica de Crecimiento y Tendencias
Se han aplicado tasas de crecimiento específicas por año para simular la evolución real del negocio:

| Año | Crecimiento vs. Año Anterior | Observaciones |
| :--- | :--- | :--- |
| 2017 | Base | Punto de partida del negocio. |
| 2020/21 | Especial | Impacto significativo por pandemia COVID-19. |
| 2022 | +1.60% | Inicio de estrategias de marketing digital y promociones. |
| 2026 | ~2025 | Datos actuales e incrementales generados dinámicamente. |

## 4. Factores Externos (Variables Exógenas)
### 4.1. Impacto de Marketing Digital (Desde 2022)
- **Campaña Activa**: Si `ads_activos == 1`, incremento de demanda entre **15% y 22%**.
- **Canales**: Gestión en Instagram (60%) y Facebook (40%).

### 4.2. Impacto Climatológico (Medellín)
- **Lluvia Moderada**: Incremento del **10% al 15%** (Efecto antojo de producto caliente).
- **Lluvia Fuerte**: Reducción del **5% al 8%** (Menor tráfico peatonal).
- **Temperatura Calibrada**: Si la temperatura media es **< 20°C**, se suma un **5%** a la demanda.

## 5. Gestión Logística y Financiera
### 5.1. Ciclos de Reabastecimiento
- El negocio repone inventario cuando el stock cae por debajo de 2.500 unidades (~50 lbs). Las entregas (Kits) se suman al stock disponible antes de la preparación diaria.

### 5.2. Estructura de Precios y Costos
- **TRM**: Influye diariamente en la volatilidad del `costo_unitario`.
- **SMLV**: Dispara los ajustes anuales de `precio_unitario`, usualmente en Febrero tras el incremento del salario mínimo en Colombia.

## 6. Arquitectura Técnica (Supabase)
La data no es estática; el script `incremental_update.py` sincroniza la nube con el día de ayer, recuperando el "último estado" conocido de bodega y precios para garantizar que la serie de tiempo nunca se rompa.

---
*Ultima actualización: 4 de marzo de 2026*
