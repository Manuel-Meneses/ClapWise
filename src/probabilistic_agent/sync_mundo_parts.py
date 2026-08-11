import os
import re
import unicodedata
import pandas as pd
from dotenv import load_dotenv
import requests
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
        if not p_str or p_str.lower() == 'nan': return 0.0
        
        # Sacamos el signo pesos si lo tiene
        p_str = p_str.replace('$', '').strip()
        
        # 1. Si Pandas lo convirtió a float y le agregó un .0 falso (ej: 800 -> "800.0")
        if p_str.endswith('.0'):
            p_str = p_str[:-2]
            
        # 2. TRADUCTOR ARGENTINO: Si tiene un punto y después 3 números, es un separador de miles! (ej: "358.000")
        if '.' in p_str and len(p_str.split('.')[-1]) == 3:
            p_str = p_str.replace('.', '')
            
        # 3. Si llega a haber una coma de centavos, la pasamos a punto (ej: 1500,50 -> 1500.50)
        p_str = p_str.replace(',', '.')
        
        # Extraemos solo lo que sea número y punto
        limpio = re.sub(r'[^\d.]', '', p_str)
        
        if limpio:
            val = float(limpio)
            
            # CORRECCIÓN AQUÍ: 
            # Si el valor es menor a 1500 (ningún repuesto vale menos de 1500 pesos hoy)
            # asumimos que el proveedor abrevió los miles (ej: 358 -> 358000)
            if 0 < val < 2000:
                val = val * 1000
                
            return val
            
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
        # 🔥 NUEVO MÉTODO DE DESCARGA: Primero lo bajamos al servidor, después lo lee Pandas
        respuesta = requests.get(url_descarga, timeout=120) 
        respuesta.raise_for_status() 
        
        with open("temp_mundo_parts.xlsx", "wb") as f:
            f.write(respuesta.content)
            
        diccionario_hojas = pd.read_excel("temp_mundo_parts.xlsx", sheet_name=None, dtype=str)
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