import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from config_pyme import FECHA_INICIO, FECHA_FIN

def generate_weather_data():
    # 1. Configuración de parámetros temporales
    date_range = pd.date_range(start=FECHA_INICIO, end=FECHA_FIN, freq='D')
    
    # 2. Definición de Fenómenos Macro (El Niño / La Niña)
    # Basado en registros históricos del IDEAM / NOAA
    # 0: Neutral, 1: El Niño (Sequía/Calor), -1: La Niña (Lluvia/Frío)
    events = {
        (2017, 1): -1, (2017, 2): -1, (2017, 3): 0,  (2017, 10): -1, (2017, 11): -1, (2017, 12): -1,
        (2018, 1): -1, (2018, 2): -1, (2018, 3): -1, (2018, 4): 0,   (2018, 9): 1,   (2018, 10): 1, (2018, 11): 1, (2018, 12): 1,
        (2019, 1): 1,  (2019, 2): 1,  (2019, 3): 1,  (2019, 4): 1,   (2019, 5): 1,   (2019, 6): 1,  (2019, 7): 0,
        (2020, 9): -1, (2020, 10): -1, (2020, 11): -1, (2020, 12): -1,
        (2021, 1): -1, (2021, 2): -1,  (2021, 3): -1,  (2021, 4): -1,  (2021, 5): -1, (2021, 10): -1, (2021, 11): -1, (2021, 12): -1,
        (2022, 1): -1, (2022, 2): -1,  (2022, 3): -1,  (2022, 4): -1,  (2022, 5): -1, (2022, 6): -1, (2022, 7): -1, (2022, 8): -1, (2022, 9): -1, (2022, 10): -1, (2022, 11): -1, (2022, 12): -1,
        (2023, 1): -1, (2023, 2): -1,  (2023, 3): 0,   (2023, 6): 1,   (2023, 7): 1,  (2023, 8): 1,  (2023, 9): 1,  (2023, 10): 1, (2023, 11): 1, (2023, 12): 1,
        (2024, 1): 1,  (2024, 2): 1,   (2024, 3): 1,   (2024, 4): 1,   (2024, 5): 1,  (2024, 10): -1, (2024, 11): -1, (2024, 12): -1,
        (2025, 1): -1, (2025, 2): -1,  (2025, 3): -1,  (2025, 6): 0
    }

    # 3. Normales Climatológicas Medellín
    # Mes: (Temp_Promedio, Prob_Lluvia)
    medellin_normals = {
        1: (22.0, 0.30), 2: (22.2, 0.35), 3: (22.3, 0.50),
        4: (22.1, 0.70), 5: (22.0, 0.75), 6: (22.4, 0.45),
        7: (22.7, 0.40), 8: (22.6, 0.45), 9: (22.1, 0.65),
        10: (21.8, 0.80), 11: (21.7, 0.75), 12: (21.9, 0.45)
    }

    results = []
    np.random.seed(42)

    for date in date_range:
        month = date.month
        year = date.year
        
        # A. Evento Macro
        fenomeno_val = events.get((year, month), 0)
        fenomeno_str = "Neutral"
        if fenomeno_val == 1: fenomeno_str = "El Niño"
        elif fenomeno_val == -1: fenomeno_str = "La Niña"
        
        # B. Temperatura
        temp_base, prob_lluvia_base = medellin_normals[month]
        
        # Impacto de Fenómeno en Temperatura
        # El Niño sube temp (+1.5), La Niña baja temp (-1.2)
        temp_impact = fenomeno_val * (1.5 if fenomeno_val == 1 else 1.2)
        temp_final = temp_base + temp_impact + np.random.normal(0, 0.5)
        
        # C. Precipitación
        # Impacto de Fenómeno en Lluvia
        # La Niña sube prob lluvia, El Niño la baja
        prob_lluvia_final = prob_lluvia_base + (fenomeno_val * -0.20) # Si Niño(1), baja prob. Si Niña(-1), sube prob.
        prob_lluvia_final = max(0.1, min(0.95, prob_lluvia_final))
        
        # Simular si llovió hoy
        lluvia_hoy = 1 if np.random.random() < prob_lluvia_final else 0
        mm_lluvia = 0
        tipo_lluvia = "Ninguna"
        
        if lluvia_hoy:
            # Si hay lluvia, determinar intensidad
            # En Medellín las lluvias son fuertes
            mm_lluvia = np.random.gamma(2, 10) # Promedio 20mm si llueve
            if mm_lluvia < 5: tipo_lluvia = "Ligera"
            elif mm_lluvia < 25: tipo_lluvia = "Moderada"
            else: tipo_lluvia = "Fuerte"

        results.append({
            'fecha': date,
            'temperatura_media': round(temp_final, 1),
            'probabilidad_lluvia': round(prob_lluvia_final, 2),
            'precipitacion_mm': round(mm_lluvia, 1),
            'tipo_lluvia': tipo_lluvia,
            'evento_macro': fenomeno_str,
            'es_dia_lluvioso': lluvia_hoy
        })

    # 4. Crear DataFrame
    df_weather = pd.DataFrame(results)
    
    # 5. Guardar CSV
    df_weather.to_csv('clima_diario.csv', index=False)
    print("Archivo 'clima_diario.csv' generado con éxito.")
    
    # 6. Gráfica
    plt.figure(figsize=(15, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df_weather['fecha'], df_weather['temperatura_media'], color='orange', alpha=0.7)
    plt.title('Evolución Temperatura Media - Medellín')
    plt.ylabel('°C')
    
    plt.subplot(2, 1, 2)
    # Media móvil de precipitación para ver temporadas
    plt.plot(df_weather['fecha'], df_weather['precipitacion_mm'].rolling(30).mean(), color='blue')
    plt.title('Precipitación Media (MA 30 días) - Medellín')
    plt.ylabel('mm')
    
    plt.tight_layout()
    plt.savefig('analisis_clima.png', dpi=150)
    print("Gráfica 'analisis_clima.png' guardada.")

if __name__ == "__main__":
    generate_weather_data()
