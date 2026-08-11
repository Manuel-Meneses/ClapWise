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

URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1c39kYssBH8TWE4JPZ8c4xy9OJ4RnsCme/edit?usp=sharing&ouid=118424615442179350058&rtpof=true&sd=true"

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

def clasificar_calidad_mundo_parts(titulo_producto):
    titulo = quitar_tildes(titulo_producto).upper()
    calidad = "ESTÁNDAR"
    
    if "SERVICE PACK" in titulo or "ORIG" in titulo:
        calidad = "SERVICE PACK"
    elif "INCELL" in titulo:
        calidad = "INCELL"
    elif "CROWN" in titulo or " MS " in titulo:
        calidad = "CROWN/MS"
    elif "OLED" in titulo or "MODULO" in titulo or "PANTALLA" in titulo:
        calidad = "OLED"
        
    if "C/M" in titulo or "CON MARCO" in titulo:
        calidad += " CON MARCO"
        
    return calidad

def sincronizar_mundo_parts():
    print("📥 Iniciando descarga de MUNDO PARTS...")
    
    url_descarga = URL_GOOGLE_SHEETS.replace("/edit?usp=sharing", "/export?format=xlsx")
    if "export?format=xlsx" not in url_descarga:
        url_descarga = URL_GOOGLE_SHEETS.split("/edit")[0] + "/export?format=xlsx"
        
    try:
        diccionario_hojas = pd.read_excel(url_descarga, sheet_name=None)
        lote_total = []
        
        for nombre_hoja, df in diccionario_hojas.items():
            if "joystick" in nombre_hoja.lower():
                print(f"⏭️ Ignorando hoja prohibida: {nombre_hoja}")
                continue
                
            print(f"📄 Procesando hoja: {nombre_hoja}...")
            
            for index, row in df.iterrows():
                for col_idx in range(len(df.columns) - 1):
                    celda_prod_raw = str(row.iloc[col_idx])
                    celda_precio_raw = str(row.iloc[col_idx + 1])
                    
                    # 🧹 ASPIRADORA EXTREMA: Mata saltos de línea (\n) y espacios múltiples
                    celda_prod = " ".join(celda_prod_raw.split())
                    celda_precio = " ".join(celda_precio_raw.split())
                    
                    if not celda_prod or celda_prod.lower() == 'nan' or len(celda_prod) < 4:
                        continue
                    if "precio" in celda_prod.lower() or "mundo parts" in celda_prod.lower():
                        continue
                        
                    # 🔋 INYECTOR DE CATEGORÍAS (Por si Mundo Parts tampoco pone la palabra)
                    if "BAT" in nombre_hoja.upper() and "BATERIA" not in celda_prod.upper():
                        celda_prod = f"Batería {celda_prod}"
                    
                    # 🚫 FILTRO DE BASURA MECÁNICA
                    prod_upper = celda_prod.upper()
                    if "MECANICO" in prod_upper and not any(buena in prod_upper for buena in ["CROWN", "PREMIUM", "OLED"]):
                        continue
                        
                    if "$" in celda_precio or celda_precio.replace('.', '').isdigit():
                        precio_num = limpiar_precio(celda_precio)
                        
                        if precio_num > 0:
                            calidad = clasificar_calidad_mundo_parts(celda_prod)
                            prod_limpio = celda_prod.replace("C/M", "CON MARCO")
                            prod_limpio = re.sub(r'(?i)/?MECANICO/?', ' ', prod_limpio).strip()
                            
                            nombre_final = f"[CALIDAD: {calidad}] {prod_limpio} - {nombre_hoja.upper()}"
                            
                            producto_db = {
                                "client_id": "proveedor_mundo_parts",
                                "nombre_consolidado": nombre_final,
                                "precio": precio_num,
                                "stock": 99
                            }
                            lote_total.append(producto_db)
                            
        lote_unico = {p['nombre_consolidado']: p for p in lote_total}.values()
        
        if lote_unico:
            print(f"\n📦 Extracción completa. {len(lote_unico)} repuestos listos de Mundo Parts.")
            supabase.table("productos").delete().eq("client_id", "proveedor_mundo_parts").execute()
            supabase.table("productos").insert(list(lote_unico)).execute()
            print("✅ Catálogo de Mundo Parts subido a Supabase exitosamente.")
        else:
            print("⚠️ No se encontraron productos con formato válido para extraer.")

    except Exception as e:
        print(f"🚨 Error crítico al sincronizar Mundo Parts: {e}")

if __name__ == "__main__":
    sincronizar_mundo_parts()