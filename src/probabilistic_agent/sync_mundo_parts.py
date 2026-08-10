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

# ⚠️ PEGÁ ACÁ EL LINK DE GOOGLE SHEETS DE MUNDO PARTS (El link largo normal para compartir)
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1c39kYssBH8TWE4JPZ8c4xy9OJ4RnsCme/edit?usp=sharing&ouid=118424615442179350058&rtpof=true&sd=true"

def limpiar_precio(precio_str):
    """Limpia el texto del precio ('$ 15.000,00' -> 15000.0)"""
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
    """Aplica la lógica de calidades incluyendo C/M (Con Marco)"""
    titulo = quitar_tildes(titulo_producto).upper()
    
    calidad = "ESTÁNDAR"
    
    # 1. Filtro base
    if "SERVICE PACK" in titulo or "ORIG" in titulo:
        calidad = "SERVICE PACK"
    elif "INCELL" in titulo:
        calidad = "INCELL"
    elif "CROWN" in titulo or " MS " in titulo:
        calidad = "CROWN/MS"
    elif "OLED" in titulo or "MODULO" in titulo or "PANTALLA" in titulo:
        calidad = "OLED"
        
    # 2. Detector de Marcos
    if "C/M" in titulo or "CON MARCO" in titulo:
        calidad += " CON MARCO"
        
    return calidad

def sincronizar_mundo_parts():
    print("📥 Iniciando descarga de MUNDO PARTS...")
    
    # Transformamos el link de compartir en un link de descarga directa Excel (.xlsx)
    url_descarga = URL_GOOGLE_SHEETS.replace("/edit?usp=sharing", "/export?format=xlsx")
    if "export?format=xlsx" not in url_descarga:
        url_descarga = URL_GOOGLE_SHEETS.split("/edit")[0] + "/export?format=xlsx"
        
    try:
        # Descargamos TODAS las hojas de una vez
        diccionario_hojas = pd.read_excel(url_descarga, sheet_name=None)
        
        lote_total = []
        
        for nombre_hoja, df in diccionario_hojas.items():
            # 🚫 REGLA DE JOA: Ignorar la hoja de Joystick
            if "joystick" in nombre_hoja.lower():
                print(f"⏭️ Ignorando hoja prohibida: {nombre_hoja}")
                continue
                
            print(f"📄 Procesando hoja: {nombre_hoja}...")
            
            # ESCÁNER TIPO "RADAR": Recorre filas y barre columnas de a pares
            for index, row in df.iterrows():
                for col_idx in range(len(df.columns) - 1):
                    celda_prod = str(row.iloc[col_idx]).strip()
                    celda_precio = str(row.iloc[col_idx + 1]).strip()
                    
                    # Filtros para ignorar vacíos, títulos y la palabra "PRECIO"
                    if not celda_prod or celda_prod.lower() == 'nan' or len(celda_prod) < 4:
                        continue
                    if "precio" in celda_prod.lower() or "mundo parts" in celda_prod.lower():
                        continue
                    
                    # 🚫 FILTRO ASESINO: Bloqueamos calidad mecánica pura
                    prod_upper = celda_prod.upper()
                    if "MECANICO" in prod_upper and not any(buena in prod_upper for buena in ["CROWN", "PREMIUM", "OLED"]):
                        continue
                        
                    # Si el producto tiene caracteres, verificamos si al lado hay un precio
                    if "$" in celda_precio or celda_precio.replace('.', '').isdigit():
                        precio_num = limpiar_precio(celda_precio)
                        
                        if precio_num > 0:
                            # Parseamos el nombre
                            calidad = clasificar_calidad_mundo_parts(celda_prod)
                            
                            # Expandimos "C/M" en el nombre para que la IA lo entienda fácil
                            prod_limpio = celda_prod.replace("C/M", "CON MARCO")
                            
                            # Borramos la palabra MECANICO si venía mezclada (ej: CROWN/MECANICO)
                            prod_limpio = re.sub(r'(?i)/?MECANICO/?', ' ', prod_limpio).strip()
                            
                            nombre_final = f"[CALIDAD: {calidad}] {prod_limpio} - {nombre_hoja.upper()}"
                            
                            producto_db = {
                                "client_id": "proveedor_mundo_parts",
                                "nombre_consolidado": nombre_final,
                                "precio": precio_num,
                                "stock": 99
                            }
                            lote_total.append(producto_db)
                            
        # Limpiamos duplicados por si acaso el escáner leyó algo dos veces
        lote_unico = {p['nombre_consolidado']: p for p in lote_total}.values()
        
        if lote_unico:
            print(f"\n📦 Extracción completa. {len(lote_unico)} repuestos listos de Mundo Parts.")
            # Borramos el catálogo viejo de Mundo Parts y subimos el nuevo
            supabase.table("productos").delete().eq("client_id", "proveedor_mundo_parts").execute()
            supabase.table("productos").insert(list(lote_unico)).execute()
            print("✅ Catálogo de Mundo Parts subido a Supabase exitosamente.")
        else:
            print("⚠️ No se encontraron productos con formato válido para extraer.")

    except Exception as e:
        print(f"🚨 Error crítico al sincronizar Mundo Parts: {e}")

if __name__ == "__main__":
    sincronizar_mundo_parts()