import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

# 👇 ¡PEGÁ ACÁ TU LINK DE GOOGLE SHEETS! (Recordá que debe terminar en /export?format=xlsx)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1NhJ69KAOtLl1hD8FxQh4umQbO8uTUySiz2EZI3-XFUE/export?format=xlsx"

def cargar_catalogo_joa():
    print("Iniciando lectura del Excel desde Google Sheets...")
    
    # 1. Leemos el archivo directo desde la nube
    df = pd.read_excel(URL_SHEET, sheet_name="celus ")
    
    # 2. Limpiamos las filas que no tienen Modelo o Precio (basura del Excel)
    df = df.dropna(subset=['Modelo', 'PRECIO'])
    
    productos_a_inyectar = []
    
    # 3. Armamos la estructura de datos
    for index, row in df.iterrows():
        modelo = str(row['Modelo']).strip()
        precio_str = str(row['PRECIO']).strip()
        detalle = str(row['Detalle ']).strip() if pd.notna(row['Detalle ']) else "Usado / Buen estado"
        
        try:
            precio_limpio = float(precio_str.replace('$', '').replace('.', '').replace(',', '.').strip())
        except ValueError:
            precio_limpio = 0
            
        nombre_completo = f"Celular a la venta: {modelo} - Detalles: {detalle}"
        
        # Aquí armas el diccionario con los nombres correctos de tu tabla
        producto_db = {
            "client_id": "3g_servicio",
            "nombre_consolidado": nombre_completo,
            "precio": precio_limpio,
            "stock": 1
        }
        productos_a_inyectar.append(producto_db)
        print(f"Listo para vectorizar: {modelo} a ${precio_limpio}")

    print(f"\nSe encontraron {len(productos_a_inyectar)} celulares listos para subir a Supabase.")
    
    try:
        # 🧹 PASO CLAVE: Borramos el catálogo local viejo de Joa para evitar duplicados
        supabase.table("productos").delete().eq("client_id", "3g_servicio").execute()
        
        # 🚀 Inyectamos el catálogo nuevo
        supabase.table("productos").insert(productos_a_inyectar).execute()
        print("✅ Catálogo actualizado con éxito (sin duplicados).")
    except Exception as e:
        print(f"❌ Error al subir: {e}")

if __name__ == "__main__":
    cargar_catalogo_joa()