import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
load_dotenv()
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(URL, KEY)

TABLAS_DIARIAS = {
    'ventas': 'ventas',
    'inventario': 'inventario_detallado',
    'finanzas': 'finanzas_pyme',
    'clima': 'clima_diario',
    'marketing': 'marketing_digital',
    'trm': 'trm_diaria'
}

TABLAS_MENSUALES = {
    'ipc_mensual': 'inflacion_mensual_ipc',
    'desempleo_mensual': 'tasa_desempleo'
}

def get_last_date(table_name):
    try:
        response = supabase.table(table_name).select("fecha").order("fecha", desc=True).limit(1).execute()
        if response.data:
            return datetime.strptime(response.data[0]['fecha'], '%Y-%m-%d').date()
        return None
    except Exception as e:
        print(f"Error consultando fecha en {table_name}: {e}")
        return None

def get_last_state():
    inv = supabase.table('inventario_detallado').select("*").order("fecha", desc=True).limit(1).execute()
    fin = supabase.table('finanzas_pyme').select("*").order("fecha", desc=True).limit(1).execute()
    trm = supabase.table('trm_diaria').select("*").order("fecha", desc=True).limit(1).execute()
    
    return {
        'kit_final_bodega': int(inv.data[0]['kit_final_bodega']) if (inv.data and inv.data[0]['kit_final_bodega'] is not None) else 3000,
        'last_price': int(fin.data[0]['precio_unitario']) if (fin.data and fin.data[0]['precio_unitario'] is not None) else 600,
        'last_cost': float(fin.data[0]['costo_unitario']) if (fin.data and fin.data[0]['costo_unitario'] is not None) else 210.0,
        'last_trm': float(trm.data[0]['trm']) if (trm.data and trm.data[0]['trm'] is not None) else 3900.0
    }

# ==========================================
# 2. GENERADORES DE DATOS
# ==========================================

def generate_daily_batch(start_date, end_date, state):
    date_range = pd.date_range(start=start_date, end=end_date)
    batch = {k: [] for k in TABLAS_DIARIAS.keys()}
    kit_ayer = state['kit_final_bodega']
    trm_act = state['last_trm']
    
    for current_date in date_range:
        d_str = current_date.strftime('%Y-%m-%d')
        y, m, wd = current_date.year, current_date.month, current_date.weekday()
        
        # A. TRM
        trm_act *= np.random.uniform(0.997, 1.003)
        batch['trm'].append({'fecha': d_str, 'trm': round(float(trm_act), 2)})

        # B. CLIMA
        temp = np.random.uniform(18.5, 23.5)
        lluvia = 1 if np.random.random() < (0.65 if m in [4,5,9,10,11] else 0.35) else 0
        precip = np.random.gamma(2, 8) if lluvia else 0.0
        tipo = 'Fuerte' if precip > 20 else ('Moderada' if precip > 5 else ('Ligera' if precip > 0 else 'Ninguna'))
        batch['clima'].append({
            'fecha': d_str, 'temperatura_media': round(float(temp), 1), 'probabilidad_lluvia': 0.5,
            'precipitacion_mm': round(float(precip), 1), 'tipo_lluvia': tipo, 'evento_macro': 'Neutral', 'es_dia_lluvioso': int(lluvia)
        })

        # C. MARKETING
        es_camp = 1 if m in [3, 4, 5, 8, 9, 10] and y >= 2022 else 0
        inv_val = int(np.random.uniform(18000, 25000)) if es_camp else 0
        batch['marketing'].append({
            'fecha': d_str, 'inversion_total': int(inv_val), 'ig_cost': int(inv_val * 0.65), 'fb_cost': int(inv_val * 0.35),
            'ig_pct': 65.0, 'fb_pct': 35.0, 'campana_activa': int(es_camp)
        })

        # D. VENTAS
        growth = 1.06 ** (y - 2017)
        demanda = int(320 * growth * (1.2 if es_camp else 1.0) * (1.15 if wd >= 4 else 1.0) * np.random.uniform(0.85, 1.15))
        es_promo = 1 if demanda < (240 * growth) and wd < 4 and np.random.random() < 0.1 else 0
        u_paga = demanda // 2 if es_promo else demanda
        batch['ventas'].append({
            'fecha': d_str, 'unidades_totales': int(demanda), 'unidades_pagas': int(u_paga), 
            'unidades_bonificadas': int(demanda - u_paga), 'es_promocion': int(es_promo), 'ads_activos': int(es_camp)
        })

        # E. INVENTARIO
        recibido = 5000 if kit_ayer < 2000 else 0
        preparados = demanda
        kit_fin = kit_ayer + recibido - int(preparados * 0.15 / 0.02)
        batch['inventario'].append({
            'fecha': d_str, 
            'kit_inicial_bodega': int(kit_ayer), 
            'lbs_iniciales_bodega': round(float(kit_ayer*0.02), 2),
            'kit_recibido': int(recibido), 
            'lbs_recibidas': int(recibido*0.02), # <-- Convertido a INT para igualar el SQL
            'lbs_totales_disponibles': round(float((kit_ayer+recibido)*0.02), 2),
            'demanda_teorica_total': int(demanda), 
            'bunuelos_preparados': int(preparados), 
            'ventas_reales_totales': int(preparados),
            'ventas_reales_pagas': int(u_paga), 
            'ventas_reales_bonificadas': int(demanda - u_paga),
            'bunuelos_desperdiciados': int(preparados*0.02), 
            'unidades_agotadas': 0, 
            'kit_final_bodega': int(kit_fin), 
            'lbs_finales_bodega': round(float(kit_fin*0.02), 2)
        })
        kit_ayer = kit_fin

        # F. FINANZAS
        costo = state['last_cost'] * (trm_act / state['last_trm'])
        batch['finanzas'].append({
            'fecha': d_str, 'precio_unitario': int(state['last_price']), 'costo_unitario': round(float(costo), 2),
            'margen_bruto': round(float(state['last_price'] - costo), 2), 
            'porcentaje_margen': round(float((state['last_price'] - costo)/state['last_price']*100), 2)
        })
        
    return batch

# ==========================================
# 3. EJECUCIÓN
# ==========================================

def run_update():
    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)
    print(f"--- INICIANDO ACTUALIZACIÓN INTEGRAL ---")

    fechas_d = {key: get_last_date(name) for key, name in TABLAS_DIARIAS.items()}
    fechas_validas = [f for f in fechas_d.values() if f is not None]
    
    if fechas_validas:
        min_date = min(fechas_validas)
        if min_date < ayer:
            start_date = min_date + timedelta(days=1)
            print(f">>> Diarias: Sincronizando desde {start_date} hasta {ayer}...")
            state = get_last_state()
            batch = generate_daily_batch(start_date, ayer, state)
            for key, table in TABLAS_DIARIAS.items():
                if batch[key]:
                    print(f"    -> [UPSERT] {table}: {len(batch[key])} registros")
                    supabase.table(table).upsert(batch[key]).execute()
        else:
            print(">>> Tablas Diarias: Al día.")

    target_m = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
    for table, col in TABLAS_MENSUALES.items():
        last_m = get_last_date(table)
        if last_m and last_m < target_m:
            to_up = []
            curr = (last_m + timedelta(days=32)).replace(day=1)
            while curr <= target_m:
                val = float(round(np.random.uniform(0.3, 0.9), 4) if table == 'ipc_mensual' else round(np.random.uniform(9.0, 12.5), 2))
                to_up.append({'fecha': curr.strftime('%Y-%m-%d'), col: val})
                curr = (curr + timedelta(days=32)).replace(day=1)
            supabase.table(table).insert(to_up).execute()
            print(f">>> {table}: Sincronizada.")
        else: print(f">>> {table}: Al día.")

    last_y_rec = get_last_date('salario_minimo_anual')
    if last_y_rec and last_y_rec.year < hoy.year:
        last_smlv_val = int(supabase.table('salario_minimo_anual').select("smlv").order("fecha", desc=True).limit(1).execute().data[0]['smlv'])
        to_up = []
        for y in range(last_y_rec.year + 1, hoy.year + 1):
            last_smlv_val = int(last_smlv_val * 1.09)
            to_up.append({'fecha': f"{y}-01-01", 'smlv': int(last_smlv_val)})
        supabase.table('salario_minimo_anual').insert(to_up).execute()
        print(f">>> salario_minimo_anual: Sincronizada.")
    else: print(">>> Salario Mínimo: Al día.")

    print("\n--- PROCESO FINALIZADO CON ÉXITO ---")

if __name__ == "__main__":
    run_update()
