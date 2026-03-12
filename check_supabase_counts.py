import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

def check_db():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: No se encontraron SUPABASE_URL o SUPABASE_KEY.")
        return

    supabase = create_client(url, key)

    tables = ['ventas', 'inventario_detallado', 'finanzas_pyme', 'clima_diario', 'marketing_digital', 'trm_diaria', 'ipc_mensual', 'desempleo_mensual', 'salario_minimo_anual']

    print(f"Connecting to {url}...")
    for table in tables:
        try:
            response = supabase.table(table).select("*", count="exact").limit(1).execute()
            count = response.count
            print(f"Tabla '{table}': {count} registros.")
        except Exception as e:
            print(f"Error consultando '{table}': {e}")

if __name__ == "__main__":
    check_db()
