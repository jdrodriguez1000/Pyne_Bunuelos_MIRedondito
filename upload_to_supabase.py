import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

def upload_data():
    # 1. Cargar credenciales
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: No se encontraron SUPABASE_URL o SUPABASE_KEY en el archivo .env")
        return

    supabase = create_client(url, key)

    # 2. Mapeo de archivos a tablas
    files_to_tables = {
        'ventas.csv': 'ventas',
        'inventario_detallado.csv': 'inventario_detallado',
        'finanzas_pyme.csv': 'finanzas_pyme',
        'clima_diario.csv': 'clima_diario',
        'marketing_digital.csv': 'marketing_digital',
        'trm_diaria.csv': 'trm_diaria',
        'ipc_mensual.csv': 'ipc_mensual',
        'desempleo_mensual.csv': 'desempleo_mensual',
        'salario_minimo_anual.csv': 'salario_minimo_anual'
    }

    # 3. Mapeo de columnas para normalización SQL
    column_mapping = {
        'buñuelos_preparados': 'bunuelos_preparados',
        'buñuelos_desperdiciados': 'bunuelos_desperdiciados',
        'campaña_activa': 'campana_activa'
    }

    # 4. Procesar y elegir carga
    for file_name, table_name in files_to_tables.items():
        if os.path.exists(file_name):
            print(f"---> Procesando {file_name}...")
            
            # Leer CSV con codificación UTF-8
            df = pd.read_csv(file_name, encoding='utf-8')
            
            # Normalizar nombres de columnas (quitar tildes y eñes)
            df = df.rename(columns=column_mapping)
            
            # Reemplazar NaN por None para que Supabase los entienda como NULL
            df = df.where(pd.notnull(df), None)
            
            # Convertir a lista de diccionarios
            data_dict = df.to_dict(orient='records')
            
            # 5. Carga por lotes (Batching) para evitar límites de la API
            batch_size = 500
            total_records = len(data_dict)
            print(f"     Subiendo {total_records} registros a '{table_name}' en lotes de {batch_size}...")
            
            for i in range(0, total_records, batch_size):
                batch = data_dict[i : i + batch_size]
                try:
                    # Usamos upsert para evitar errores de duplicidad si se re-ejecuta
                    supabase.table(table_name).upsert(batch).execute()
                    percent = min(100, round((i + batch_size) / total_records * 100, 1))
                    print(f"     Progreso: {percent}%", end='\r')
                except Exception as e:
                    print(f"\n[ERROR] Tabla '{table_name}' batch {i}: {e}")
                    break
            print(f"\n     Carga de '{table_name}' completada.")
        else:
            print(f"[Omitido] El archivo {file_name} no existe.")

    print("\nPROCESO FINALIZADO CON ÉXITO.")

if __name__ == "__main__":
    upload_data()
