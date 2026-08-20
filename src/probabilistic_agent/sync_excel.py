import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1JnYi79BaOgkfrfyC8f9cXfzFSxeo9ZjhYwPP0iM8rcg/edit?usp=sharing"

def limpiar_precio(precio_str):
    try:
        p_str = str(precio_str).replace('$', '').replace(',', '.').strip()
        if not p_str or p_str.lower() == 'nan': return 0.0
        val = float(p_str)
        return val if val > 0 else 0.0
    except:
        return 0.0

def sincronizar_todo():
    print("📥 Iniciando descarga del sistema unificado de Joa...")
    
    # Transformamos el link para que descargue directamente el Excel
    url_descarga = URL_GOOGLE_SHEETS.replace("/edit?usp=sharing", "/export?format=xlsx")
    if "export?format=xlsx" not in url_descarga:
        url_descarga = URL_GOOGLE_SHEETS.split("/edit")[0] + "/export?format=xlsx"
        
    try:
        respuesta = requests.get(url_descarga, timeout=30) 
        respuesta.raise_for_status() 
        
        with open("temp_joa.xlsx", "wb") as f:
            f.write(respuesta.content)
            
        diccionario_hojas = pd.read_excel("temp_joa.xlsx", sheet_name=None)
        
        # ==========================================
        # 1. PROCESAR LA CALCULADORA FINANCIERA
        # ==========================================
        print("🧮 Procesando Calculadora Financiera...")
        df_calc = diccionario_hojas.get("Calculadora")
        
        dto_efectivo = 0.10
        rec_3_cuotas = 0.18
        
        if df_calc is not None:
            # Buscamos en toda la hoja los parámetros
            for _, row in df_calc.iterrows():
                celda_nombre = str(row.iloc[0]).lower()
                celda_valor = str(row.iloc[1]).strip()
                
                if "descuento efectivo" in celda_nombre:
                    try: dto_efectivo = float(celda_valor.replace('%', '')) / 100 if float(celda_valor) > 1 else float(celda_valor)
                    except: pass
                elif "recargo 3 cuotas" in celda_nombre:
                    try: rec_3_cuotas = float(celda_valor.replace('%', '')) / 100 if float(celda_valor) > 1 else float(celda_valor)
                    except: pass

        reglas_matematicas = {
            "descuento_efectivo": dto_efectivo,
            "recargo_3_cuotas": rec_3_cuotas
        }
        
        supabase.table("configuracion_clientes").upsert({
            "client_id": "matriz_calculo_interna",
            "reglas_calculadora": json.dumps(reglas_matematicas)
        }).execute()
        
        # ==========================================
        # 2. PROCESAR INFO ESTÁTICA DEL LOCAL
        # ==========================================
        print("📍 Procesando Info Estática...")
        df_info = diccionario_hojas.get("Info_estatica")
        texto_info_estatica = "INFORMACIÓN ESTÁTICA DEL LOCAL:\n"
        
        if df_info is not None:
            for _, row in df_info.iterrows():
                dato = str(row.iloc[0]).strip()
                detalle = str(row.iloc[1]).strip()
                if dato != "nan" and detalle != "nan" and "Dato" not in dato:
                    texto_info_estatica += f"- {dato}: {detalle}\n"
                    
        supabase.table("configuracion_clientes").upsert({
            "client_id": "3g_servicio",
            "reglas_calculadora": texto_info_estatica
        }).execute()

        # ==========================================
        # 3. PROCESAR LOS REPUESTOS (EL CORAZÓN DEL SISTEMA)
        # ==========================================
        print("📱 Procesando Catálogo de Repuestos...")
        df_rep = diccionario_hojas.get("Repuestos")
        lote_total = []
        
        if df_rep is not None:
            # Empezamos a leer desde la fila 2 para saltar los encabezados raros de Joa
            for index in range(2, len(df_rep)):
                row = df_rep.iloc[index]
                
                modelo = str(row.iloc[0]).strip().upper()
                if not modelo or modelo == 'NAN' or modelo == 'SAMSUNG' or modelo == 'MOTOROLA':
                    continue
                
                precio_pantalla = limpiar_precio(row.iloc[2]) # Columna Pantallas
                precio_bateria = limpiar_precio(row.iloc[3])  # Columna Baterias
                precio_pin = limpiar_precio(row.iloc[4])      # Columna Pin Carga
                
                # Armamos los repuestos independientemente
                if precio_pantalla > 0:
                    lote_total.append({
                        "client_id": "proveedor_joaquin",
                        "nombre_consolidado": f"[PANTALLA] {modelo}",
                        "precio": precio_pantalla,
                        "stock": 99
                    })
                    
                if precio_bateria > 0:
                    lote_total.append({
                        "client_id": "proveedor_joaquin",
                        "nombre_consolidado": f"[BATERIA] {modelo}",
                        "precio": precio_bateria,
                        "stock": 99
                    })
                    
                if precio_pin > 0:
                    lote_total.append({
                        "client_id": "proveedor_joaquin",
                        "nombre_consolidado": f"[PIN CARGA] {modelo}",
                        "precio": precio_pin,
                        "stock": 99
                    })
        
        if lote_total:
            print(f"📦 Se encontraron {len(lote_total)} repuestos listos. Subiendo a Supabase...")
            # Borramos el catálogo viejo de este proveedor
            supabase.table("productos").delete().eq("client_id", "proveedor_joaquin").execute()
            
            # Subimos en lotes de a 500 por seguridad
            tamanio_lote = 500
            for i in range(0, len(lote_total), tamanio_lote):
                caja = lote_total[i : i + tamanio_lote]
                supabase.table("productos").insert(caja).execute()
                
            print("✅ ¡Sincronización completa! Todo el sistema se actualizó correctamente.")
        else:
            print("⚠️ No se encontraron precios en la hoja de Repuestos.")

    except Exception as e:
        import traceback
        print(f"🚨 Error crítico al sincronizar: {traceback.format_exc()}")

if __name__ == "__main__":
    sincronizar_todo()