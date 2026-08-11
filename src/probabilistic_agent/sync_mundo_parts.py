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

# ⚠️ PEGÁ ACÁ EL LINK DE GOOGLE SHEETS DE MUNDO PARTS (Asegurate de usar tu link real largo)
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1c39kYssBH8TWE4JPZ8c4xy9OJ4RnsCme/edit?usp=sharing"

def limpiar_precio(precio_str):
    try:
        p_str = str(precio_str).strip()
        
        # Si tiene el símbolo de pesos, extraemos los números directo
        if "$" in p_str:
            limpio = re.sub(r'[^\d]', '', p_str)
            return float(limpio)
        
        # Si es un número puro desde Excel (Traductor Argentino)
        try:
            val = float(p_str)
            # Si Python lee "3.5" (porque el Excel tenía 3.500), lo acomodamos a miles.
            if 0 < val < 100:
                val = val * 1000
            return val
        except ValueError:
            limpio = re.sub(r'[^\d]', '', p_str)
            if limpio:
                return float(limpio)
            return 0.0
            
    except Exception:
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
            encontrados_en_hoja = 0
            
            for index, row in df.iterrows():
                for col_idx in range(len(df.columns) - 1):
                    celda_prod_raw = str(row.iloc[col_idx])
                    celda_precio_raw = str(row.iloc[col_idx + 1])
                    
                    celda_prod = " ".join(celda_prod_raw.split())
                    celda_precio = " ".join(celda_precio_raw.split())
                    
                    if not celda_prod or celda_prod.lower() == 'nan' or len(celda_prod) < 4:
                        continue
                    if "precio" in celda_prod.lower() or "mundo parts" in celda_prod.lower():
                        continue
                        
                    # INYECTOR DE BATERÍAS
                    if "BAT" in nombre_hoja.upper() and "BATERIA" not in celda_prod.upper():
                        celda_prod = f"BATERIA {celda_prod}"
                    
                    prod_upper = celda_prod.upper()
                    if "MECANICO" in prod_upper and not any(buena in prod_upper for buena in ["CROWN", "PREMIUM", "OLED"]):
                        continue
                        
                    # EL RADAR DETECTA SI HAY DINERO AL LADO (Regla corregida)
                    if "$" in celda_precio or celda_precio.replace('.', '').replace(',', '').isdigit():
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
                            encontrados_en_hoja += 1
                            
            print(f"   -> ✔️ Se encontraron {encontrados_en_hoja} repuestos en {nombre_hoja}.")
                            
        # Limpiamos duplicados exactos
        lote_unico = list({p['nombre_consolidado']: p for p in lote_total}.values())
        total_repuestos = len(lote_unico)
        
        if total_repuestos > 0:
            print(f"\n📦 Extracción completa. Intentando subir {total_repuestos} repuestos a Supabase...")
            supabase.table("productos").delete().eq("client_id", "proveedor_mundo_parts").execute()
            
            # SUBIDA EN CAJAS DE A 500 PARA QUE SUPABASE NO FALLE
            tamanio_lote = 500
            for i in range(0, total_repuestos, tamanio_lote):
                caja = lote_unico[i : i + tamanio_lote]
                supabase.table("productos").insert(caja).execute()
                print(f"   -> Subida caja {i//tamanio_lote + 1}: {len(caja)} repuestos.")
                
            print("✅ Catálogo de Mundo Parts subido a Supabase exitosamente.")
        else:
            print("⚠️ No se encontraron productos.")

    except Exception as e:
        print(f"🚨 Error crítico al sincronizar Mundo Parts: {e}")

if __name__ == "__main__":
    sincronizar_mundo_parts()