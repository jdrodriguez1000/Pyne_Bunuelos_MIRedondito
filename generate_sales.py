import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from config_pyme import FECHA_INICIO, FECHA_FIN

def generate_synthetic_sales():
    # 1. Configuración de parámetros temporales
    date_range = pd.date_range(start=FECHA_INICIO, end=FECHA_FIN, freq='D')
    
    # 2. Definición de niveles de ventas base por año
    # Empezamos con 200 en 2017
    sales_levels = {2017: 200}
    
    # Aplicar crecimientos anuales según lo solicitado
    sales_levels[2018] = sales_levels[2017] * 1.0102
    sales_levels[2019] = sales_levels[2018] * 1.02
    # Para 2020, calculamos un nivel base antes del impacto pandémico
    sales_levels[2020] = sales_levels[2019] * 1.012 # Asumo un crecimiento base pequeño antes de la caída
    sales_levels[2021] = sales_levels[2020] * 1.013
    sales_levels[2022] = sales_levels[2021] * 1.016
    sales_levels[2023] = sales_levels[2022] * 1.0155
    sales_levels[2024] = sales_levels[2023] * 1.017
    sales_levels[2025] = sales_levels[2024] * 1.019
    sales_levels[2026] = sales_levels[2025] # Similar al 2025

    # 3. Generar la serie base con estacionalidades
    import holidays
    co_holidays = holidays.Colombia()
    base_sales_series = []
    
    for date in date_range:
        current_year = date.year
        base_val = sales_levels[current_year]
        
        # --- A. Estacionalidad Mensual ---
        # Diciembre (+40%), Enero, Junio, Julio (+20%)
        month_multipliers = {
            12: 1.40,  # Diciembre: Tope
            1: 1.20,   # Enero
            6: 1.15,   # Junio
            7: 1.15,   # Julio
        }
        month_multiplier = month_multipliers.get(date.month, 0.90) # Meses valle: 0.90
        base_val *= month_multiplier
        
        # --- B. Estacionalidad Semanal ---
        # Domingo (+30%), Sábado (+20%), Viernes (+10%)
        # weekday(): 0=Lunes, 4=Viernes, 5=Sábado, 6=Domingo
        weekly_multipliers = {
            6: 1.30, # Domingo
            5: 1.20, # Sábado
            4: 1.10, # Viernes
        }
        weekday_multiplier = weekly_multipliers.get(date.weekday(), 0.85) # Lunes-Jueves: 0.85
        
        # --- C. Días Festivos ---
        # Si es festivo, ventas comparables a un sábado (+20%)
        is_holiday = date in co_holidays
        if is_holiday:
            weekday_multiplier = max(weekday_multiplier, 1.20)
            
        base_val *= weekday_multiplier

        # --- D. Efecto Quincenas, Primas y Fechas Especiales ---
        special_multiplier = 1.0
        
        # 1. Quincena mitad de mes (15-16) y fin de mes (30-31)
        if date.day in [15, 16, 30, 31]:
            special_multiplier = 1.15
            
        # 2. Días de Prima (15 al 20 de Junio y Diciembre)
        if date.month in [6, 12] and 15 <= date.day <= 20:
            special_multiplier = max(special_multiplier, 1.20)

        # 3. Fechas Especiales con nivel de DOMINGO (+30%)
        # A. Novenas Navideñas (16 al 23 de Diciembre)
        is_novena = (date.month == 12 and 16 <= date.day <= 23)
        
        # B. Jueves y Viernes Santo
        # Buscamos en los nombres de los festivos de Colombia
        holiday_name = co_holidays.get(date)
        is_semana_santa = holiday_name and ("Jueves Santo" in holiday_name or "Viernes Santo" in holiday_name)
        
        # C. Feria de las Flores (Medellín) - Típicamente primera semana de agosto
        # Simulamos del 1 al 10 de agosto
        is_feria_flores = (date.month == 8 and 1 <= date.day <= 10)
        
        if is_novena or is_semana_santa or is_feria_flores:
            # Suben a niveles de un domingo (reemplazamos el multiplier semanal si es necesario)
            # Para simplificar, si cae en estos días, el multiplicador especial es 1.30
            special_multiplier = max(special_multiplier, 1.30)
            
        base_val *= special_multiplier
        
        # --- E. Impacto de Pandemia (Mayo 2020 a Abril 2021) ---
        pandemic_start = datetime(2020, 5, 1)
        pandemic_end = datetime(2021, 4, 30)
        
        if pandemic_start <= date <= pandemic_end:
            days_in_pandemic = (pandemic_end - pandemic_start).days
            day_num = (date - pandemic_start).days
            multiplier = 1.0 - (0.55 * np.sin(np.pi * day_num / days_in_pandemic))
            base_val = base_val * multiplier
            
        base_sales_series.append(base_val)

    
    # 6. Generar Result SET Final con Lógica de Promoción y Marketing
    results = []
    np.random.seed(42)
    
    # --- NUEVO: Cargar factores externos para ajustar demanda ---
    try:
        df_weather = pd.read_csv('clima_diario.csv')
        df_marketing = pd.read_csv('marketing_digital.csv')
        # Asegurar que coincidan las fechas para el merge
        df_weather['fecha'] = pd.to_datetime(df_weather['fecha']).dt.strftime('%Y-%m-%d')
        df_marketing['fecha'] = pd.to_datetime(df_marketing['fecha']).dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar archivos externos. Usando demanda base. Error: {e}")
        df_weather = None
        df_marketing = None

    for i, date in enumerate(date_range):
        date_str = date.strftime('%Y-%m-%d')
        year = date.year
        month = date.month
        weekday = date.weekday() # 0:Lunes, 6:Domingo
        
        # 1. Base Estacional (Simulación de crecimiento del negocio)
        # El negocio crece un 3% anual
        growth_factor = 1 + (year - 2017) * 0.03
        base_demand = 200 * growth_factor
        
        # 2. Efecto Día de la Semana
        # Fines de semana (V, S, D) venden más
        day_effect = 1.0
        if weekday == 4: day_effect = 1.4 # Viernes
        elif weekday == 5: day_effect = 1.8 # Sábado
        elif weekday == 6: day_effect = 1.6 # Domingo
        
        # 3. Efecto Mes (Temporada alta en Diciembre y Enero)
        month_effect = 1.0
        if month == 12: month_effect = 1.6
        elif month == 1: month_effect = 1.3
        
        # 4. Cálculo de Demanda Base antes de factores externos
        demanda_dia = base_demand * day_effect * month_effect
        
        # --- NUEVO: Factores Externos (Marketing, Clima, Temperatura) ---
        external_multiplier = 1.0
        ads_activos = 0 # Initialize ads_activos for this day
        
        # A. Marketing y Promoción
        if df_marketing is not None:
            mkt_row = df_marketing[df_marketing['fecha'] == date_str]
            if not mkt_row.empty:
                ads_activos = mkt_row['campaña_activa'].values[0]
                if ads_activos == 1:
                    # REGLA 1: Si hay campaña activa, aumento entre 15% y 22%
                    external_multiplier *= np.random.uniform(1.15, 1.22)
        
        # B. Clima (Lluvia)
        if df_weather is not None:
            w_row = df_weather[df_weather['fecha'] == date_str]
            if not w_row.empty:
                tipo_lluvia = w_row['tipo_lluvia'].values[0]
                temp = w_row['temperatura_media'].values[0]
                
                # REGLA 2: Lluvia moderada (+10-15%), Lluvia fuerte (-5-8%)
                if tipo_lluvia == 'Moderada':
                    external_multiplier *= np.random.uniform(1.10, 1.15)
                elif tipo_lluvia == 'Fuerte':
                    external_multiplier *= np.random.uniform(0.92, 0.95)
                
                # REGLA 3: Temperatura < 20°C (+5%)
                if temp < 20:
                    external_multiplier *= 1.05

        demanda_dia *= external_multiplier
        
        # 5. Ruido Aleatorio (Variabilidad diaria natural)
        demanda_dia *= np.random.uniform(0.9, 1.1)
        
        # 6. Definir si es un día de promoción (Basado en demanda y fecha)
        # Promoción si la demanda es baja y no es fin de semana (estrategia comercial)
        es_promocion = 0
        if demanda_dia < (250 * growth_factor) and weekday < 4:
            # 10% de probabilidad de tirar una promo en días bajos
            if np.random.random() < 0.10:
                es_promocion = 1
        
        # 7. Distribución de Unidades
        unidades_totales = int(demanda_dia)
        
        if es_promocion == 1:
            # Si hay promoción, el total se divide en partes iguales
            # Aseguramos que sea par para la igualdad
            if unidades_totales % 2 != 0:
                unidades_totales += 1
            
            p_pagas = unidades_totales // 2
            p_bonificadas = p_pagas
        else:
            p_pagas = unidades_totales
            p_bonificadas = 0
        
        results.append({
            'fecha': date_str,
            'unidades_totales': unidades_totales,
            'unidades_pagas': p_pagas,
            'unidades_bonificadas': p_bonificadas,
            'es_promocion': es_promocion,
            'ads_activos': ads_activos
        })

    # 7. Crear DataFrame
    df = pd.DataFrame(results)
    
    # 8. Guardar Archivo CSV
    csv_filename = 'ventas.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"Archivo '{csv_filename}' actualizado con impacto de Marketing.")
    
    # 9. Gráfica de Evolución
    df['fecha'] = pd.to_datetime(df['fecha'])
    plt.figure(figsize=(15, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df['fecha'], df['unidades_totales'], color='#d62728', alpha=0.3, label='Unidades Totales')
    plt.plot(df['fecha'], df['unidades_pagas'], color='#2ca02c', alpha=0.6, label='Unidades Pagas')
    plt.title('Impacto de Marketing Digital y 2x1 en la Demanda', fontsize=14)
    plt.legend()
    plt.xlabel('Año', fontsize=12)
    plt.ylabel('Unidades', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plot_filename = 'evolucion_ventas_promociones.png'
    plt.savefig(plot_filename, dpi=150)
    print(f"Gráfica de promociones '{plot_filename}' guardada.")
    
    print("\nResumen Estadístico (Unidades Totales por Año):")
    print(df.groupby(df['fecha'].dt.year)['unidades_totales'].agg(['mean', 'min', 'max']))


if __name__ == "__main__":
    generate_synthetic_sales()
