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

# ⚠️ TUS DOS LINKS PUBLICADOS (.CSV)
URL_CSV_MATRIZ = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQURuzYgPzF-_Uf9khnmEz36mVaMZQdg6UVsvdKFNbe1aA6YMDBfFqdZX4DeK1cAlyldNH72nFqsTk/pub?gid=256169068&single=true&output=csv"
URL_CSV_INFO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVs9TGz9Er9UT26VQz8zLZv_uWyZRER2ZhEi8lsbCH2h7BaSjCYQMtRt7gYFi5X2Gfz76oEVYr6Jed/pub?gid=1169996528&single=true&output=csv"

def sincronizar_calculadora():
    print("📥 Descargando datos desde Google Sheets...")
    
    try:
        # ==========================================
        # 1. DESCARGAMOS LA MATRIZ MATEMÁTICA (NUEVO SISTEMA DE TRAMOS)
        # ==========================================
        
        # Funciones antibalas para limpiar formatos
        def limpiar_dinero(valor):
            if pd.isna(valor) or str(valor).lower().strip() == 'nan': return 0.0
            v = str(valor).replace('$', '').strip()
            if v.endswith(',00'): v = v[:-3]
            if v.endswith('.00'): v = v[:-3]
            v = v.replace('.', '').replace(',', '')
            try:
                return float(v)
            except:
                return 0.0

        def limpiar_porcentaje(valor):
            if pd.isna(valor) or str(valor).lower().strip() == 'nan': return 0.0
            v = str(valor).replace('%', '').replace(',', '.').strip()
            try:
                val = float(v)
                return val / 100 if val > 1 else val
            except:
                return 0.0

        df_matriz = pd.read_csv(URL_CSV_MATRIZ)
        
        tramos = []
        dto_efectivo = 0.15  # Valores por defecto por si falla el Excel
        rec_3_cuotas = 0.18
        rec_6_cuotas = 0.26
        
        for index, row in df_matriz.iterrows():
            # A) Buscar los porcentajes financieros (Columna 1 y 2 en el DataFrame)
            col1 = str(row.iloc[1]).strip()
            if col1 == "Descuento efectivo (%)":
                dto_efectivo = limpiar_porcentaje(row.iloc[2])
            elif col1 == "Recargo 3 cuotas (%)":
                rec_3_cuotas = limpiar_porcentaje(row.iloc[2])
            elif col1 == "Recargo 6 cuotas (%)":
                rec_6_cuotas = limpiar_porcentaje(row.iloc[2])
                
            # B) Buscar los tramos de precios (Columnas 4, 5 y 6 en el DataFrame)
            desde_str = str(row.iloc[4]).strip()
            
            # Filtramos para no leer títulos ni celdas vacías
            if desde_str and desde_str.lower() != "nan" and desde_str != "Desde ($)":
                try:
                    desde = limpiar_dinero(row.iloc[4])
                    hasta = limpiar_dinero(row.iloc[5])
                    sumar = limpiar_dinero(row.iloc[6])
                    
                    if hasta > 0:
                        tramos.append({
                            "desde": desde,
                            "hasta": hasta,
                            "sumar": sumar
                        })
                except Exception as e:
                    continue 
                    
        # Empaquetamos todo en un diccionario ordenado
        reglas_matematicas = {
            "tramos": tramos,
            "descuento_efectivo": dto_efectivo,
            "recargo_3_cuotas": rec_3_cuotas,
            "recargo_6_cuotas": rec_6_cuotas
        }
                
        # Guardamos la nueva matriz matemática para Python
        supabase.table("configuracion_clientes").upsert({
            "client_id": "matriz_calculo_interna",
            "reglas_calculadora": json.dumps(reglas_matematicas)
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
        
        print("🚀 ¡Sincronización completa! La info del local y la NUEVA matriz están actualizadas.\n")
        
    except Exception as e:
        print(f"🚨 Error crítico al sincronizar: {e}")

if __name__ == "__main__":
    sincronizar_calculadora()