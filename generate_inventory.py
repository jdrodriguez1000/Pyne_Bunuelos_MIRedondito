import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def generate_inventory_data():
    # 1. Cargar la data de ventas (demanda teórica)
    try:
        df_sales = pd.read_csv('ventas.csv')
        df_sales['fecha'] = pd.to_datetime(df_sales['fecha'])
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'ventas.csv'. Ejecuta primero 'generate_sales.py'.")
        return

    # 2. Parámetros de Simulación de Inventario
    conversion_rate = 50  # 1 lb = 50 buñuelos
    kit_bodega = 3000     # Empezamos con stock inicial de kit para enero
    desperdicio_previo = 55 # Lo que mencionaste del ciclo anterior
    results = []
    
    np.random.seed(42)

    dates = df_sales['fecha'].tolist()
    demands = df_sales['unidades_totales'].tolist()
    pagas = df_sales['unidades_pagas'].tolist()
    promociones = df_sales['es_promocion'].tolist()
    
    for i, date in enumerate(dates):
        # A. Entregas de Kit (Materia Prima)
        entrega_kit = 0
        lbs_recibidas = 0
        
        # Logística de reabastecimiento
        is_last_day = date.day == date.days_in_month
        if is_last_day:
            future_demand = sum(demands[i+1 : i+15]) if i+1 < len(demands) else 0
            if future_demand > 0:
                target_kit = future_demand * np.random.uniform(1.0, 1.10)
                lbs_recibidas = int(np.ceil(target_kit / conversion_rate))
                entrega_kit = lbs_recibidas * conversion_rate
        elif date.day == 14:
            days_until_end = date.days_in_month - 14
            future_demand = sum(demands[i+1 : i + 1 + days_until_end]) if i+1 < len(demands) else 0
            if future_demand > 0:
                target_kit = future_demand * np.random.uniform(1.0, 1.10)
                lbs_recibidas = int(np.ceil(target_kit / conversion_rate))
                entrega_kit = lbs_recibidas * conversion_rate

        # The initial inventory of day T is exactly what was left at the end of T-1
        stock_inicial_kit = kit_bodega
        
        # Now we receive the new supply
        kit_bodega += entrega_kit
        
        # Total available for the day (Initial + Received) BEFORE preparation
        total_disponible_hoy = kit_bodega
        
        # B. Decisión de Preparación
        demanda_esperada = demands[i] * np.random.uniform(0.92, 1.08)
        preparados_hoy = int(min(kit_bodega, demanda_esperada))
        
        # C. Venta Real vs Demanda Teórica (Unidades Totales)
        demanda_total_mercado = demands[i]
        
        # Vendemos lo mínimo entre lo que preparamos y lo que sale de la tienda
        ventas_totales_efectivas = min(preparados_hoy, demanda_total_mercado)
        
        # D. Proporción de pagas vs bonificadas en la venta real
        # Si no pudimos vender todo lo pedido, reducimos proporcionalmente
        ratio = ventas_totales_efectivas / demanda_total_mercado if demanda_total_mercado > 0 else 0
        
        if promociones[i] == 1:
            # Promotion Rule: REAL Paid and REAL Bonus units must be equal
            reales_pagas = int(pagas[i] * ratio)
            reales_bonificadas = reales_pagas
            # Real total is the sum of both
            ventas_totales_efectivas = reales_pagas + reales_bonificadas
        else:
            reales_pagas = int(pagas[i] * ratio)
            reales_bonificadas = ventas_totales_efectivas - reales_pagas
        
        # D. Agotados y Desperdicios
        # Agotados: Gente que quería pero no había preparados (demand units actually requested vs effective sales)
        agotados = max(0, demanda_total_mercado - ventas_totales_efectivas)
        
        # Desperdicio: Buñuelos preparados que no se vendieron (SE PIERDEN)
        desperdicio_dia = max(0, preparados_hoy - ventas_totales_efectivas)
        
        # E. Actualización de Bodega (Solo descontamos lo que se PREPARÓ)
        kit_bodega -= preparados_hoy
        
        results.append({
            'fecha': date,
            'kit_inicial_bodega': stock_inicial_kit,
            'lbs_iniciales_bodega': round(stock_inicial_kit / conversion_rate, 2),
            'kit_recibido': entrega_kit,
            'lbs_recibidas': lbs_recibidas,
            'lbs_totales_disponibles': round(total_disponible_hoy / conversion_rate, 2),
            'demanda_teorica_total': demanda_total_mercado,
            'buñuelos_preparados': preparados_hoy,
            'ventas_reales_totales': ventas_totales_efectivas,
            'ventas_reales_pagas': reales_pagas,
            'ventas_reales_bonificadas': reales_bonificadas,
            'buñuelos_desperdiciados': desperdicio_dia,
            'unidades_agotadas': agotados,
            'kit_final_bodega': kit_bodega,
            'lbs_finales_bodega': round(kit_bodega / conversion_rate, 2)
        })

    # 4. Crear DataFrame
    df_inv = pd.DataFrame(results)
    
    # 5. Guardar CSV
    inv_filename = 'inventario_detallado.csv'
    df_inv.to_csv(inv_filename, index=False)
    print(f"Archivo '{inv_filename}' generado con la nueva lógica de desperdicio.")
    
    # 6. Gráfica
    plt.figure(figsize=(15, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df_inv['fecha'], df_inv['kit_final_bodega'], color='blue', label='Stock Kit (Bodega)')
    plt.title('Gestión de Materia Prima vs Desperdicio de Producto Terminado')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.bar(df_inv['fecha'], df_inv['buñuelos_desperdiciados'], color='orange', label='Desperdicio (Buñuelos no vendidos)')
    plt.bar(df_inv['fecha'], df_inv['unidades_agotadas'], color='red', alpha=0.5, label='Agotados (Venta perdida)')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analisis_desperdicio.png', dpi=150)


if __name__ == "__main__":
    generate_inventory_data()
