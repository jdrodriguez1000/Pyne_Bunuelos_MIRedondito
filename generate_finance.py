import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from config_pyme import FECHA_INICIO, FECHA_FIN

def generate_finance_data():
    # 1. Cargar datos macro desde múltiples archivos
    try:
        df_trm = pd.read_csv('trm_diaria.csv')
        df_ipc = pd.read_csv('ipc_mensual.csv')
        df_desempleo = pd.read_csv('desempleo_mensual.csv')
        df_smlv = pd.read_csv('salario_minimo_anual.csv')
        
        # Convertir fecha trm a datetime y extraer temporalidad
        df_trm['fecha'] = pd.to_datetime(df_trm['fecha'])
        df_trm['year'] = df_trm['fecha'].dt.year
        df_trm['month'] = df_trm['fecha'].dt.month
        
        # Pre-procesar archivos mensuales y anuales para el cruce
        for df in [df_ipc, df_desempleo, df_smlv]:
            df['fecha_parsed'] = pd.to_datetime(df['fecha'])
            df['year_map'] = df['fecha_parsed'].dt.year
            df['month_map'] = df['fecha_parsed'].dt.month
            df.drop(columns=['fecha', 'fecha_parsed'], inplace=True)
        
        # Unir todo en un solo dataframe diario para facilitar la lógica existente
        df_macro = pd.merge(df_trm, df_ipc.rename(columns={'year_map':'year', 'month_map':'month'}), on=['year', 'month'], how='left')
        df_macro = pd.merge(df_macro, df_desempleo.rename(columns={'year_map':'year', 'month_map':'month'}), on=['year', 'month'], how='left')
        df_macro = pd.merge(df_macro, df_smlv.rename(columns={'year_map':'year'}), on=['year'], how='left')
        
        # Ordenar por fecha
        df_macro = df_macro.sort_values('fecha').reset_index(drop=True)
        
    except Exception as e:
        print(f"Error: Ejecuta primero generate_macro.py. Detalles: {e}")
        return

    results = []
    
    # Precios y costos iniciales 2017
    current_price = 580.0
    current_cost_base = 207.5 # Promedio entre 200 y 215
    
    np.random.seed(42)

    for i, row in df_macro.iterrows():
        date = row['fecha']
        year = date.year
        month = date.month
        day = date.day
        
        # --- A. Lógica de Precios (Saltos en Feb 1 y Jul 1) ---
        if year == 2017:
            if month >= 7:
                current_price = 600.0
            else:
                current_price = 580.0
        else:
            # Para años > 2017, el precio sube proporcionalmente a la inflación y SMLV
            if (month == 2 and day == 1) or (month == 7 and day == 1):
                inc_factor = 1.0
                if month == 2:
                    # Comparar SMLV con año anterior
                    smlv_this = row['smlv']
                    # Buscamos el SMLV del año pasado usando el dataframe procesado df_smlv
                    mask_prev = df_smlv['year_map'] == year - 1
                    smlv_prev = df_smlv[mask_prev]['smlv'].values[0] if mask_prev.any() else smlv_this
                    ratio_smlv = smlv_this / smlv_prev if smlv_prev > 0 else 1.05
                    inc_factor = 1.0 + (ratio_smlv - 1.0) * 0.6 
                else:
                    # Julio: Sube según inflación acumulada (aprox)
                    inc_factor = 1.03 
                
                current_price = round(current_price * inc_factor / 10) * 10 
        
        # --- B. Lógica de Costos (Fluctuación diaria e inflacionaria) ---
        ipc_impact = 1 + (row['inflacion_mensual_ipc'] / 100)
        current_cost_base *= ipc_impact
        
        # Ruido diario basado en TRM y azar
        trm_noise = (row['trm'] / 3500) * np.random.uniform(-0.5, 1.5)
        daily_fluctuation = np.random.uniform(0.97, 1.03) 
        
        costo_final = (current_cost_base * daily_fluctuation) + trm_noise
        
        # Asegurar márgenes lógicos
        costo_final = min(costo_final, current_price * 0.6)
        costo_final = max(costo_final, current_price * 0.2)

        results.append({
            'fecha': date,
            'precio_unitario': int(current_price),
            'costo_unitario': round(costo_final, 2),
            'margen_bruto': round(current_price - costo_final, 2),
            'porcentaje_margen': round(((current_price - costo_final) / current_price) * 100, 2)
        })

    # 3. Crear DataFrame
    df_fin = pd.DataFrame(results)
    
    # 4. Guardar CSV
    df_fin.to_csv('finanzas_pyme.csv', index=False)
    print("Archivo 'finanzas_pyme.csv' generado con éxito con base en los nuevos archivos macro.")
    
    # 5. Visualización
    plt.figure(figsize=(15, 7))
    plt.plot(df_fin['fecha'], df_fin['precio_unitario'], label='Precio de Venta', drawstyle='steps-post', linewidth=2)
    plt.plot(df_fin['fecha'], df_fin['costo_unitario'], label='Costo de Producción', alpha=0.5)
    plt.fill_between(df_fin['fecha'], df_fin['costo_unitario'], df_fin['precio_unitario'], color='gray', alpha=0.1, label='Margen Bruto')
    plt.title('Evolución de Precios y Costos - Tu Buñuelito', fontsize=14)
    plt.ylabel('Pesos ($)')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('analisis_precios_costos.png', dpi=150)
    print("Gráfica 'analisis_precios_costos.png' guardada.")

if __name__ == "__main__":
    generate_finance_data()
