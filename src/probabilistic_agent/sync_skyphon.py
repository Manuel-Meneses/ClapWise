import os
import re
import unicodedata
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

# ⚠️ PEGÁ ACÁ EL LINK DE GOOGLE SHEETS DE SKYPHON
URL_GOOGLE_SHEETS_SKYPHON = "https://docs.google.com/spreadsheets/d/1ewZCtjpTRNzsOLQXArrzc8ayMGms5m9F/edit?usp=sharing&ouid=118424615442179350058&rtpof=true&sd=true"

def limpiar_precio(precio_str):
    try:
        limpio = re.sub(r'[^\d]', '', str(precio_str))
        return float(limpio)
    except:
        return 0.0

def quitar_tildes(texto):
    try:
        texto = str(texto)
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    except:
        return texto

def clasificar_calidad_skyphon(titulo_producto):
    titulo = quitar_tildes(titulo_producto).upper()
    calidad = "ESTÁNDAR"
    
    # 1. Filtro base (SIN MECANICO)
    if "SERVICE PACK" in titulo or "ORIG" in titulo:
        calidad = "SERVICE PACK"
    elif "INCELL" in titulo:
        calidad = "INCELL"
    elif any(palabra in titulo for palabra in ["CROWN", "MS ", "PREMIUM"]):
        calidad = "CROWN/MS"
    elif "OLED" in titulo or "MODULO" in titulo or "PANTALLA" in titulo:
        calidad = "OLED"
        
    # 2. Detector de Marcos
    if "C/M" in titulo or "CON MARCO" in titulo or "C/MARCO" in titulo:
        calidad += " CON MARCO"
        
    return calidad

def sincronizar_skyphon():
    print("📥 Iniciando descarga de SKYPHON...")
    
    url_descarga = URL_GOOGLE_SHEETS_SKYPHON.replace("/edit?usp=sharing", "/export?format=xlsx")
    if "export?format=xlsx" not in url_descarga:
        url_descarga = URL_GOOGLE_SHEETS_SKYPHON.split("/edit")[0] + "/export?format=xlsx"
        
    try:
        diccionario_hojas = pd.read_excel(url_descarga, sheet_name=None)
        lote_total = []
        
        for nombre_hoja, df in diccionario_hojas.items():
            print(f"📄 Procesando hoja: {nombre_hoja}...")
            
            for index, row in df.iterrows():
                try:
                    celda_prod = str(row.iloc[1]).strip()
                    celda_precio = str(row.iloc[2]).strip()
                except IndexError:
                    continue 
                    
                if not celda_prod or celda_prod.lower() in ['nan', 'descripción', 'codigo', 'módulos']:
                    continue
                    
                # 🚫 FILTRO DE BASURA: Si dice mecanico y no tiene alternativas (Crown/Premium), lo volamos
                prod_upper = celda_prod.upper()
                if "MECANICO" in prod_upper and not any(buena in prod_upper for buena in ["CROWN", "PREMIUM", "OLED"]):
                    continue # Se ignora completamente
                    
                if "$" in celda_precio or celda_precio.replace('.', '').isdigit():
                    precio_num = limpiar_precio(celda_precio)
                    
                    if precio_num > 0:
                        calidad = clasificar_calidad_skyphon(celda_prod)
                        
                        # Limpiamos el texto para la base de datos
                        prod_limpio = celda_prod.replace("C/M", "CON MARCO").replace("c/m", "CON MARCO")
                        # Borramos la palabra MECANICO si venía mezclada con CROWN
                        prod_limpio = re.sub(r'(?i)/?MECANICO/?', ' ', prod_limpio).strip()
                        
                        nombre_final = f"[CALIDAD: {calidad}] {prod_limpio} - SKYPHON"
                        
                        producto_db = {
                            "client_id": "proveedor_skyphon",
                            "nombre_consolidado": nombre_final,
                            "precio": precio_num,
                            "stock": 99
                        }
                        lote_total.append(producto_db)
                            
        lote_unico = {p['nombre_consolidado']: p for p in lote_total}.values()
        
        if lote_unico:
            print(f"\n📦 Extracción completa. {len(lote_unico)} repuestos listos de Skyphon.")
            supabase.table("productos").delete().eq("client_id", "proveedor_skyphon").execute()
            supabase.table("productos").insert(list(lote_unico)).execute()
            print("✅ Catálogo de Skyphon subido a Supabase exitosamente.")
        else:
            print("⚠️ No se encontraron productos con formato válido para extraer.")

    except Exception as e:
        print(f"🚨 Error crítico al sincronizar Skyphon: {e}")

if __name__ == "__main__":
    sincronizar_skyphon()