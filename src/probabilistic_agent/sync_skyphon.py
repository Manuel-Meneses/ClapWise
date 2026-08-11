import os
import re
import unicodedata
import pandas as pd
import requests # 🔥 Usamos requests para evitar que Google corte la descarga
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
        p_str = str(precio_str).replace('$', '').strip()
        if not p_str or p_str.lower() == 'nan': return 0.0
        
        # Regla argentina: Si tiene punto y 3 números atrás (ej: 15.500), es separador de miles
        if '.' in p_str and len(p_str.split('.')[-1]) == 3:
            p_str = p_str.replace('.', '')
        # Si tiene coma (centavos), la pasamos a punto
        p_str = p_str.replace(',', '.')
        
        limpio = re.sub(r'[^\d.]', '', p_str)
        if limpio:
            return float(limpio)
        return 0.0
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
    
    if "SERVICE PACK" in titulo or "ORIG" in titulo:
        calidad = "SERVICE PACK"
    elif "INCELL" in titulo:
        calidad = "INCELL"
    elif any(palabra in titulo for palabra in ["CROWN", "MS ", "PREMIUM"]):
        calidad = "CROWN/MS"
    elif "OLED" in titulo or "MODULO" in titulo or "PANTALLA" in titulo:
        calidad = "OLED"
        
    if "C/M" in titulo or "CON MARCO" in titulo or "C/MARCO" in titulo:
        calidad += " CON MARCO"
        
    return calidad

def sincronizar_skyphon():
    print("📥 Iniciando descarga de SKYPHON...")
    
    url_descarga = URL_GOOGLE_SHEETS_SKYPHON.replace("/edit?usp=sharing", "/export?format=xlsx")
    if "export?format=xlsx" not in url_descarga:
        url_descarga = URL_GOOGLE_SHEETS_SKYPHON.split("/edit")[0] + "/export?format=xlsx"
        
    try:
        print("⏳ Descargando archivo pesado desde Google Sheets...")
        respuesta = requests.get(url_descarga, timeout=120) 
        respuesta.raise_for_status() 
        
        with open("temp_skyphon.xlsx", "wb") as f:
            f.write(respuesta.content)
            
        # Leemos el Excel como texto para evitar que Pandas redondee mal los números
        diccionario_hojas = pd.read_excel("temp_skyphon.xlsx", sheet_name=None, dtype=str)
        lote_total = []
        
        for nombre_hoja, df in diccionario_hojas.items():
            print(f"📄 Procesando hoja: {nombre_hoja}...")
            hoja_upper = quitar_tildes(nombre_hoja).upper()
            
            for index, row in df.iterrows():
                # 🔥 RADAR INTELIGENTE: Escaneamos de izquierda a derecha.
                # Restamos 2 al límite para asegurarnos de que la celda actual tenga al menos dos celdas más a la derecha.
                for col_idx in range(len(df.columns) - 2):
                    celda_prod_raw = str(row.iloc[col_idx])
                    celda_precio_1_raw = str(row.iloc[col_idx + 1]) # Precio 1
                    celda_precio_2_raw = str(row.iloc[col_idx + 2]) # Precio 2 (Efectivo/Lista)
                
                    celda_prod = " ".join(celda_prod_raw.split())
                    celda_precio_1 = " ".join(celda_precio_1_raw.split())
                    celda_precio_2 = " ".join(celda_precio_2_raw.split())
                        
                    # Filtramos basura, códigos cortos o encabezados
                    if not celda_prod or len(celda_prod) < 3 or celda_prod.lower() in ['nan', 'descripción', 'codigo', 'código', 'módulos', 'precio', 'efectivo', 'lista', 'modelo', 'marca']:
                        continue
                    
                    precio_1_num = 0.0
                    precio_2_num = 0.0
                        
                    # Comprobamos si la primera columna contigua parece dinero
                    if "$" in celda_precio_1 or celda_precio_1.replace('.', '').replace(',', '').isdigit():
                        precio_1_num = limpiar_precio(celda_precio_1)
                    
                    # Comprobamos si la segunda columna contigua parece dinero
                    if "$" in celda_precio_2 or celda_precio_2.replace('.', '').replace(',', '').isdigit():
                        precio_2_num = limpiar_precio(celda_precio_2)
                        
                    # 🔥 MATEMÁTICA PURA: Nos quedamos siempre con el precio más alto
                    precio_final = max(precio_1_num, precio_2_num)
                    
                    # Si detectamos un precio válido, confirmamos que esto es un repuesto
                    if precio_final > 0:
                        prod_upper = celda_prod.upper()
                        nombre_base = celda_prod
                        
                        # 🔋 INYECTOR DE CONTEXTO POR HOJA (Tapas y Baterías)
                        if "TAPA" in hoja_upper and "TAPA" not in prod_upper:
                            nombre_base = f"TAPA {celda_prod}"
                        elif "BATERIA" in hoja_upper and "BATERIA" not in prod_upper and "BAT" not in prod_upper:
                            nombre_base = f"BATERIA {celda_prod}"
                            
                        # 🚫 FILTRO DE BASURA MECÁNICA
                        if "MECANICO" in nombre_base.upper() and not any(buena in nombre_base.upper() for buena in ["CROWN", "PREMIUM", "OLED"]):
                            break # Rompemos el ciclo para ignorar esta fila completa
                            
                        calidad = clasificar_calidad_skyphon(nombre_base)
                        prod_limpio = nombre_base.replace("C/M", "CON MARCO").replace("c/m", "CON MARCO")
                        prod_limpio = re.sub(r'(?i)/?MECANICO/?', ' ', prod_limpio).strip()
                        
                        nombre_consolidado = f"[CALIDAD: {calidad}] {prod_limpio} - SKYPHON"
                        
                        producto_db = {
                            "client_id": "proveedor_skyphon",
                            "nombre_consolidado": nombre_consolidado,
                            "precio": precio_final,
                            "stock": 99
                        }
                        lote_total.append(producto_db)
                        
                        # 🛑 Frenamos el escaneo horizontal en esta fila porque ya encontramos el repuesto
                        break
                        
        lote_unico = {p['nombre_consolidado']: p for p in lote_total}.values()
        
        if lote_unico:
            print(f"\n📦 Extracción completa. {len(lote_unico)} repuestos listos de Skyphon.")
            supabase.table("productos").delete().eq("client_id", "proveedor_skyphon").execute()
            
            # 🔥 SUBIDA EN CAJAS DE 500
            lista_final = list(lote_unico)
            tamanio_lote = 500
            for i in range(0, len(lista_final), tamanio_lote):
                caja = lista_final[i : i + tamanio_lote]
                supabase.table("productos").insert(caja).execute()
                print(f"   -> Subida caja {i//tamanio_lote + 1}: {len(caja)} repuestos.")
                
            print("✅ Catálogo de Skyphon subido a Supabase exitosamente.")
        else:
            print("⚠️ No se encontraron productos con formato válido para extraer.")

    except Exception as e:
        print(f"🚨 Error crítico al sincronizar Skyphon: {e}")

if __name__ == "__main__":
    sincronizar_skyphon()