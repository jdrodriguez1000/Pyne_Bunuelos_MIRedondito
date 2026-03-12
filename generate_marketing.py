import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from config_pyme import FECHA_INICIO, FECHA_FIN

def generate_marketing_data():
    # 1. Configuración de parámetros temporales
    date_range = pd.date_range(start=FECHA_INICIO, end=FECHA_FIN, freq='D')
    
    results = []
    
    # 2. Lógica de inversión
    # 2022: 15,000 / día
    # Incremento: 2,000 / año
    base_costs = {
        2022: 15000,
        2023: 17000,
        2024: 19000,
        2025: 21000,
        2026: 23000
    }

    for date in date_range:
        current_year = date.year
        inversion_total = 0
        ig_pct = 0
        fb_pct = 0
        ig_cost = 0
        fb_cost = 0
        campaign_active = 0
        
        # Solo hay inversión desde 2022
        if current_year >= 2022:
            # Definir ventanas de inversión
            # Ventana 1: 20 días antes de Abril (Marzo 12) hasta Mayo 25
            promo1_start = datetime(current_year, 3, 12)
            promo1_end = datetime(current_year, 5, 25)
            
            # Ventana 2: 20 días antes de Septiembre (Agosto 12) hasta Octubre 25
            promo2_start = datetime(current_year, 8, 12)
            promo2_end = datetime(current_year, 10, 25)
            
            if (promo1_start <= date <= promo1_end) or (promo2_start <= date <= promo2_end):
                campaign_active = 1
                base_daily = base_costs.get(current_year, 23000)
                # Variabilidad pequeña en la inversión diaria (+/- 5%)
                inversion_total = int(base_daily * np.random.uniform(0.95, 1.05))
                
                # Split Instagram (65%-70%)
                ig_pct = np.random.uniform(0.65, 0.70)
                fb_pct = 1 - ig_pct
                
                ig_cost = int(inversion_total * ig_pct)
                fb_cost = inversion_total - ig_cost

        results.append({
            'fecha': date,
            'inversion_total': inversion_total,
            'ig_cost': ig_cost,
            'fb_cost': fb_cost,
            'ig_pct': round(ig_pct * 100, 2),
            'fb_pct': round(fb_pct * 100, 2),
            'campaña_activa': campaign_active
        })

    # 3. Crear DataFrame
    df_marketing = pd.DataFrame(results)
    
    # 4. Guardar CSV
    df_marketing.to_csv('marketing_digital.csv', index=False)
    print("Archivo 'marketing_digital.csv' generado con éxito.")
    
    # 5. Visualización
    plt.figure(figsize=(15, 6))
    plt.plot(df_marketing['fecha'], df_marketing['inversion_total'], color='purple', label='Inversión Diaria Total')
    plt.fill_between(df_marketing['fecha'], df_marketing['inversion_total'], color='purple', alpha=0.1)
    plt.title('Inversión en Marketing Digital (Facebook e Instagram) - Tu Buñuelito', fontsize=14)
    plt.ylabel('Pesos COP')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('analisis_marketing.png', dpi=150)
    print("Gráfica 'analisis_marketing.png' guardada.")

if __name__ == "__main__":
    generate_marketing_data()
