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

# ⚠️ ACÁ VAN TUS DOS LINKS PUBLICADOS (.CSV)
URL_CSV_MATRIZ = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVs9TGz9Er9UT26VQz8zLZv_uWyZRER2ZhEi8lsbCH2h7BaSjCYQMtRt7gYFi5X2Gfz76oEVYr6Jed/pub?gid=0&single=true&output=csv"
URL_CSV_INFO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVs9TGz9Er9UT26VQz8zLZv_uWyZRER2ZhEi8lsbCH2h7BaSjCYQMtRt7gYFi5X2Gfz76oEVYr6Jed/pub?gid=1169996528&single=true&output=csv"

def sincronizar_calculadora():
    print("📥 Descargando datos desde Google Sheets...")
    
    try:
        # ==========================================
        # 1. DESCARGAMOS LA MATRIZ MATEMÁTICA
        # ==========================================
        df_matriz = pd.read_csv(URL_CSV_MATRIZ)
        matriz_precios = []
        for index, row in df_matriz.iterrows():
            try:
                min_cost = float(str(row.iloc[0]).replace('$', '').replace('.', '').replace(',', '').strip())
                mo = float(str(row.iloc[1]).replace('$', '').replace('.', '').replace(',', '').strip())
                dto = float(str(row.iloc[2]).replace('%', '').replace(',', '.').strip())
                rec = float(str(row.iloc[3]).replace('%', '').replace(',', '.').strip())
                if dto > 1: dto = dto / 100
                if rec > 1: rec = rec / 100
                matriz_precios.append({"min": min_cost, "mo": mo, "dto": dto, "rec": rec})
            except: continue 
                
        # Guardamos la matriz matemática para Python
        supabase.table("configuracion_clientes").upsert({
            "client_id": "matriz_calculo_interna",
            "reglas_calculadora": json.dumps(matriz_precios)
        }).execute()

        # ==========================================
        # 2. DESCARGAMOS LA INFO ESTÁTICA DEL LOCAL
        # ==========================================
        df_info = pd.read_csv(URL_CSV_INFO)
        texto_info_estatica = "INFORMACIÓN ESTÁTICA DEL LOCAL:\n"
        
        # Leemos la tabla de 2 columnas (A=Dato, B=Detalle)
        for index, row in df_info.iterrows():
            dato = str(row.iloc[0]).strip()
            detalle = str(row.iloc[1]).strip()
            
            # Si la fila no está vacía, la sumamos al texto
            if dato != "nan" and detalle != "nan":
                texto_info_estatica += f"- {dato}: {detalle}\n"
                
        # Le sumamos la regla estricta de que la IA no calcule nada
        texto_final_ia = f"""
        {texto_info_estatica}
        
        REGLA FINANCIERA (ESTRICTA): Los precios que te entregue el sistema ya son los FINALES. NO le sumes mano de obra ni apliques descuentos, entrégalos exactamente como el sistema te los arroja.
        """
        
        # Guardamos TODO el contexto de la empresa para que Gemini lo lea
        supabase.table("configuracion_clientes").upsert({
            "client_id": "3g_servicio",
            "reglas_calculadora": texto_final_ia
        }).execute()
        
        print("🚀 ¡Sincronización completa! La info del local y la matriz están actualizadas.\n")
        
    except Exception as e:
        print(f"🚨 Error crítico al sincronizar: {e}")

if __name__ == "__main__":
    sincronizar_calculadora()