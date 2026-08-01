import os
import json
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

# ⚠️ ACÁ PEGÁS EL LINK .CSV QUE TE DA GOOGLE SHEETS AL PUBLICAR LA HOJA
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVs9TGz9Er9UT26VQz8zLZv_uWyZRER2ZhEi8lsbCH2h7BaSjCYQMtRt7gYFi5X2Gfz76oEVYr6Jed/pub?gid=0&single=true&output=csv"

def sincronizar_calculadora():
    print("📥 Descargando la matriz matemática desde Google Sheets...")
    
    try:
        # Leemos el CSV desde la web
        df = pd.read_csv(URL_CSV)
        
        matriz_precios = []
        
        # Recorremos fila por fila para armar el cerebro matemático
        for index, row in df.iterrows():
            try:
                # Nos aseguramos de limpiar signos $, % y comas por si Joa los tipea
                min_cost = float(str(row.iloc[0]).replace('$', '').replace('.', '').replace(',', '').strip())
                mo = float(str(row.iloc[1]).replace('$', '').replace('.', '').replace(',', '').strip())
                
                dto_str = str(row.iloc[2]).replace('%', '').replace(',', '.').strip()
                rec_str = str(row.iloc[3]).replace('%', '').replace(',', '.').strip()
                
                dto = float(dto_str)
                rec = float(rec_str)
                
                # Si el excel dice "16" en vez de "0.16", lo dividimos por 100
                if dto > 1: dto = dto / 100
                if rec > 1: rec = rec / 100
                
                matriz_precios.append({
                    "min": min_cost,
                    "mo": mo,
                    "dto": dto,
                    "rec": rec
                })
            except Exception as e:
                # Si hay una fila vacía o un texto raro, la ignora y sigue
                continue 
                
        # Guardamos la matriz como un JSON en Supabase (bajo un cliente falso para que sea fácil de leer)
        data_matriz = {
            "client_id": "matriz_calculo_interna",
            "reglas_calculadora": json.dumps(matriz_precios)
        }
        
        # También le aclaramos a la IA de 3G Servicio que ya no tiene que hacer cálculos
        data_ia = {
            "client_id": "3g_servicio",
            "reglas_calculadora": "REGLA FINANCIERA: Los precios que te entregue el sistema ya son los FINALES. NO le sumes mano de obra ni apliques descuentos, entrégalos exactamente como el sistema te los arroja."
        }
        
        supabase.table("configuracion_clientes").upsert(data_matriz).execute()
        supabase.table("configuracion_clientes").upsert(data_ia).execute()
        
        print("🚀 ¡Sincronización completa! La matriz de Joa está inyectada en la base de datos.\n")
        
    except Exception as e:
        print(f"🚨 Error crítico al sincronizar la calculadora: {e}")

if __name__ == "__main__":
    sincronizar_calculadora()