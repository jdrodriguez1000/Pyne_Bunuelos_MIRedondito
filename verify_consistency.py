import pandas as pd

def verify_data_consistency():
    # 1. Cargar archivos
    try:
        df_sales = pd.read_csv('ventas.csv')
        df_inv = pd.read_csv('inventario_detallado.csv')
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return

    print("--- Verificación de Consistencia de Datos ---")

    # Verificación 1: Ventas (totales = pagas + bonificadas)
    df_sales['calc_total'] = df_sales['unidades_pagas'] + df_sales['unidades_bonificadas']
    diff_sales = df_sales[df_sales['unidades_totales'] != df_sales['calc_total']]
    
    if diff_sales.empty:
        print("VOK: En ventas.csv -> unidades_totales == unidades_pagas + unidades_bonificadas")
    else:
        print(f"ERROR: En ventas.csv hay {len(diff_sales)} filas con inconsistencias.")
        print(diff_sales.head())

    # Verificación 2: Inventario (demanda_teorica == ventas_reales + agotadas)
    df_inv['calc_demanda'] = df_inv['ventas_reales_totales'] + df_inv['unidades_agotadas']
    diff_inv = df_inv[df_inv['demanda_teorica_total'] != df_inv['calc_demanda']]
    
    if diff_inv.empty:
        print("VOK: En inventario_detallado.csv -> demanda_teorica_total == ventas_reales_totales + unidades_agotadas")
    else:
        print(f"ERROR: En inventario_detallado.csv hay {len(diff_inv)} filas con inconsistencias.")
        print(diff_inv[['fecha', 'demanda_teorica_total', 'ventas_reales_totales', 'unidades_agotadas', 'calc_demanda']].head())

    # Verificación 3: Cruce entre archivos (unidades_totales == demanda_teorica_total)
    df_merge = pd.merge(df_sales[['fecha', 'unidades_totales']], 
                        df_inv[['fecha', 'demanda_teorica_total']], 
                        on='fecha')
    
    diff_merge = df_merge[df_merge['unidades_totales'] != df_merge['demanda_teorica_total']]
    
    if diff_merge.empty:
        print("VOK: El cruce es correcto -> unidades_totales (Ventas) == demanda_teorica_total (Inventario)")
    else:
        print(f"ERROR: Hay {len(diff_merge)} fechas donde los totales no coinciden entre archivos.")

if __name__ == "__main__":
    verify_data_consistency()
