import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

URL_SHEET = "https://docs.google.com/spreadsheets/d/1NhJ69KAOtLl1hD8FxQh4umQbO8uTUySiz2EZI3-XFUE/export?format=xlsx"

def sincronizar_calculadora():
    print("📥 Leyendo la lógica financiera desde Google Sheets...")
    
    try:
        df = pd.read_excel(URL_SHEET, sheet_name="Calculadora precios service")
        
        # 1. Extraemos forzando a que sean números reales (evita que un error de tipeo rompa el bot)
        mano_obra_baja = int(pd.to_numeric(df.iloc[5, 1], errors='coerce') or 0)
        mano_obra_media = int(pd.to_numeric(df.iloc[14, 1], errors='coerce') or 0)
        mano_obra_alta = int(pd.to_numeric(df.iloc[23, 1], errors='coerce') or 0)
        
        # 2. Limpieza de porcentajes (Cubre si Joa pone '16', '16%' o '0.16')
        val_efectivo = str(df.iloc[7, 2]).replace('%', '').strip()
        val_tarjeta = str(df.iloc[8, 2]).replace('%', '').strip()
        
        desc_float = float(val_efectivo)
        porcentaje_efectivo = int(desc_float * 100) if desc_float < 1 else int(desc_float)
            
        recargo_float = float(val_tarjeta)
        porcentaje_tarjeta = int(recargo_float * 100) if recargo_float < 1 else int(recargo_float)

        reglas_dinamicas = f"""
        REGLAS PARA COTIZAR REPARACIONES (LA CALCULADORA INTERNA ACTUALIZADA):
        
        Paso A) Calcula el Precio de Lista MENTALMENTE (Costo repuesto + Mano de Obra):
        - Si el repuesto cuesta hasta $38.000, suma ${mano_obra_baja}.
        - Si el repuesto cuesta entre $39.000 y $45.000, suma ${mano_obra_media}.
        - Si el repuesto cuesta más de $45.000, suma ${mano_obra_alta}.

        Paso B) Calcula los 3 precios finales para el cliente a partir del Precio de Lista:
        1. Precio de Lista (Transferencia/Débito): Resultado exacto del Paso A.
        2. Precio Efectivo: Quítale un {porcentaje_efectivo}% al Precio de Lista.
        3. Precio Tarjeta (3 Cuotas): Súmale un {porcentaje_tarjeta}% al Precio de Lista (y divide en 3 para la cuota).
        """
        
        data = {
            "client_id": "3g_servicio",
            "reglas_calculadora": reglas_dinamicas
        }
        
        supabase.table("configuracion_clientes").upsert(data).execute()
        print("🚀 Sincronización completa. El cerebro financiero de Joa está en la nube.\n")
        
    except Exception as e:
        print(f"🚨 Error crítico al sincronizar la calculadora de Joa: {e}")
        print("⚠️ Avisale a Joa que no modifique la estructura de las filas en el Excel.")

if __name__ == "__main__":
    sincronizar_calculadora()