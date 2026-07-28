import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargamos las credenciales desde tu archivo .env[cite: 4]
load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def scraper_i2c_definitivo():
    print("🚀 Iniciando extracción masiva adaptada a tu tabla exacta...")
    
    # 🧹 PASO CLAVE: Vaciamos el catálogo viejo de i2c ANTES de empezar a raspar
    try:
        print("Borrando lista de precios vieja del proveedor i2c...")
        supabase.table("productos").delete().eq("client_id", "proveedor_i2c").execute()
        print("✅ Base de datos limpia. Lista para recibir los precios de hoy.")
    except Exception as e:
        print(f"🚨 Error al intentar limpiar la base de datos: {e}")
        print("Frenando ejecución para evitar duplicados.")
        return 

    # Establecemos los encabezados y variables iniciales[cite: 4]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    pagina = 1
    total_ingresados = 0
    
    # Iniciamos el ciclo para recorrer las páginas[cite: 4]
    while True:
        url = "https://www.i2cmayorista.com/productos/" if pagina == 1 else f"https://www.i2cmayorista.com/productos/?page={pagina}"
        print(f"📄 Procesando página {pagina}...")
        
        try:
            respuesta = requests.get(url, headers=headers)
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            break

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        productos = soup.find_all(class_=lambda c: c and ('js-item-product' in c or 'item' == c))
        
        if not productos:
            print("🏁 No se encontraron más contenedores. Fin del catálogo.")
            break
            
        lote_repuestos = []
        
        for producto in productos:
            etiqueta_nombre = producto.find(class_=lambda c: c and 'js-item-name' in c)
            etiqueta_precio = producto.find(class_=lambda c: c and 'js-price-display' in c)
            
            if not etiqueta_nombre or not etiqueta_precio:
                continue
                
            nombre = etiqueta_nombre.text.strip()
            precio_texto = etiqueta_precio.text.strip()
            
            try:
                precio_limpio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.'))
            except ValueError:
                continue
                
            if precio_limpio <= 0:
                continue
                
            # Usamos las columnas EXACTAS de tu tabla[cite: 4]
            producto_db = {
                "client_id": "proveedor_i2c", 
                "nombre_consolidado": nombre,
                "precio": precio_limpio,
                "stock": 99  # Stock ficticio alto porque es proveedor[cite: 4]
            }
            lote_repuestos.append(producto_db)
        
        if not lote_repuestos:
            break
            
        # Inyectamos el lote en Supabase[cite: 4]
        try:
            supabase.table("productos").insert(lote_repuestos).execute()
            total_ingresados += len(lote_repuestos)
            print(f"✅ {len(lote_repuestos)} repuestos guardados.")
        except Exception as e:
            print(f"❌ Error al guardar en BD: {e}")
            break
        
        pagina += 1
        time.sleep(1) 
        
    print(f"\n🎉 ¡MISIÓN CUMPLIDA! Total de repuestos inyectados: {total_ingresados}")

if __name__ == "__main__":
    scraper_i2c_definitivo()