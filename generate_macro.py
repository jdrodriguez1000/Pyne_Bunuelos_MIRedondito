import pandas as pd
import numpy as np
import os

from config_pyme import FECHA_INICIO, FECHA_FIN

def generate_macro_data():
    # 1. Configuración de parámetros temporales
    date_range = pd.date_range(start=FECHA_INICIO, end=FECHA_FIN, freq='D')
    
    # 2. Diccionarios de referencia histórica aproximada (Colombia)
    smlv_values = {
        2017: 737717, 2018: 781242, 2019: 828116, 2020: 877803,
        2021: 908526, 2022: 1000000, 2023: 1160000, 2024: 1300000,
        2025: 1420000, 2026: 1512300 
    }
    
    inflacion_anual = {
        2017: 4.09, 2018: 3.18, 2019: 3.80, 2020: 1.61, 
        2021: 5.62, 2022: 13.12, 2023: 9.28, 2024: 5.50,
        2025: 4.20, 2026: 3.80
    }

    desempleo_base = {
        2017: 9.4, 2018: 9.7, 2019: 10.5, 2020: 15.9, 
        2021: 13.7, 2022: 11.2, 2023: 10.2, 2024: 9.8,
        2025: 9.5, 2026: 9.3
    }

    # 3. Listas para cada archivo
    trm_list = []
    ipc_list = []
    desempleo_list = []
    smlv_list = []

    # TRM Inicial
    trm_actual = 3000.0
    np.random.seed(42)

    last_month = -1
    last_year = -1

    for date in date_range:
        year = date.year
        month = date.month
        
        # A. TRM (DIARIA)
        drift = 0.2 if year < 2022 else 0.5
        if year >= 2024: drift = -0.1
        trm_actual += np.random.normal(drift, 15.0)
        trm_actual = max(2800, trm_actual)
        
        trm_list.append({
            'fecha': date.strftime('%Y-%m-%d'),
            'trm': round(trm_actual, 2)
        })

        # B. IPC y DESEMPLEO (MENSUAL)
        if month != last_month:
            # IPC
            ipc_mensual = inflacion_anual.get(year) / 12
            ipc_list.append({
                'fecha': f"{year}-{month:02d}-01",
                'inflacion_mensual_ipc': round(ipc_mensual, 4)
            })
            
            # Desempleo
            base = desempleo_base.get(year)
            seasonal_unemp = np.sin(2 * np.pi * month / 12) * 0.5
            desempleo_list.append({
                'fecha': f"{year}-{month:02d}-01",
                'tasa_desempleo': round(base + seasonal_unemp, 2)
            })
            last_month = month

        # C. SMLV (ANUAL)
        if year != last_year:
            smlv_list.append({
                'fecha': f"{year}-01-01",
                'smlv': smlv_values.get(year)
            })
            last_year = year

    # 4. Guardar los 4 archivos
    pd.DataFrame(trm_list).to_csv('trm_diaria.csv', index=False)
    pd.DataFrame(ipc_list).to_csv('ipc_mensual.csv', index=False)
    pd.DataFrame(desempleo_list).to_csv('desempleo_mensual.csv', index=False)
    pd.DataFrame(smlv_list).to_csv('salario_minimo_anual.csv', index=False)

    print("Archivos generados con éxito:")
    print("- trm_diaria.csv (Diario)")
    print("- ipc_mensual.csv (Mensual)")
    print("- desempleo_mensual.csv (Mensual)")
    print("- salario_minimo_anual.csv (Anual)")

if __name__ == "__main__":
    generate_macro_data()
