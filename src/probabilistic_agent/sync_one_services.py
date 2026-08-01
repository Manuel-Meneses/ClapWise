import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

def sincronizar_one_services():
    print("📥 Iniciando Auto-Login en One Services...\n")
    
    # 1. Creamos una "Sesión" que guarda las cookies automáticamente
    session = requests.Session()
    
    # Le ponemos un disfraz para que parezca un navegador real (Chrome)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.one-service.com.ar/index.php"
    })
    
    # 2. Datos de inicio de sesión (REEMPLAZÁ ESTO CON TUS DATOS)
    login_data = {
        "user": os.environ.get("ONE_USER", "Juanmamontoya"), 
        "password": os.environ.get("ONE_PASS", "123456"), # Si no funciona, cambiá "pass" por "password"
        "accion": "login" # Opcional, pero muchas web PHP lo necesitan
    }
    
    login_url = "https://www.one-service.com.ar/index.php"
    
    # Hacemos el POST (Enviamos el formulario y entramos)
    print("🔑 Intentando entrar con tu usuario...")
    session.post(login_url, data=login_data)
    
    # Verificamos si nos dieron la credencial
    cookies_actuales = session.cookies.get_dict()
    if "trusted_session" in cookies_actuales:
        print("✅ ¡Login exitoso! Credenciales nuevas obtenidas automáticamente.")
    else:
        print("⚠️ Cuidado: No veo la cookie de sesión. O la contraseña está mal, o Cloudflare frenó el login. (Cookies: {})".format(cookies_actuales))
    
    # 3. Vamos a buscar los productos usando tu UID fijo y la sesión nueva
    uid = "2604"
    api_key = "3b62b791096437bab1d01d4ccbdd5c58"
    
    page = 1
    total_pages = 1 
    lote_total = []
    
    while page <= total_pages:
        print(f"📄 Procesando página {page} de {total_pages}...")
        url = f"https://www.one-service.com.ar/api/productos.php?uid={uid}&api={api_key}&page={page}"
        
        try:
            # Usamos session.get() en vez de requests.get() para que viaje con el token fresco
            respuesta = session.get(url)
            
            if respuesta.status_code != 200:
                print(f"❌ Error HTTP {respuesta.status_code}.")
                break
                
            datos_json = respuesta.json()
            
            if 'error' in datos_json:
                print(f"🚨 La API respondió con error: {datos_json['error']}")
                break
                
            if page == 1:
                total_pages = datos_json.get('total_pages', 1)
                
            productos = datos_json.get('body', [])
            print(f"🔎 Productos encontrados en esta página: {len(productos)}")
            
            for item in productos:
                if not item.get('permite_pedido', False):
                    continue
                    
                categoria = str(item.get('categoria', '')).strip().upper()
                marca = str(item.get('marca', '')).strip().upper()
                producto = str(item.get('producto', '')).strip().upper()
                
                # Descartamos iPhone para este proveedor
                if "IPHONE" in marca or "IPHONE" in producto:
                    continue
                
                # 🚫 FILTRO ESTRICTO DE BASURA: 
                # Le agregamos espacios a " HD " para que no corte palabras que tengan "hd" por casualidad
                producto_con_espacios = f" {producto} "
                if any(basura in producto_con_espacios for basura in [" MECANICO ", " OLED SMALL ", " HD ", " HD+ ", " FHD "]):
                    continue
                
                # Para la base de datos, guardamos el nombre limpio, las prioridades las calculará el bot en vivo
                nombre_completo = f"{categoria} {marca} {producto}"
                
                calidad_tag = ""
                if "SOFT" in producto:
                    calidad_tag = "[CALIDAD: SOFT OLED (Primera Opción)]"
                elif "HARD" in producto:
                    calidad_tag = "[CALIDAD: HARD OLED]"
                elif "OLED" in producto and "MARCO" in producto:
                    calidad_tag = "[CALIDAD: OLED CON MARCO]"
                elif "OLED" in producto or "PREMIUM" in producto or "ORIG" in producto:
                    calidad_tag = "[CALIDAD: OLED / ORIGINAL]"
                elif "SUNLONG" in producto or "JK" in producto:
                    calidad_tag = "[CALIDAD: SUNLONG (Segunda Instancia/Alternativa Superior)]"
                elif "INCELL" in producto:
                    calidad_tag = "[CALIDAD: INCELL (Básica/Para zafar)]"
                else:
                    calidad_tag = "[CALIDAD: ESTÁNDAR]"
                    
                nombre_completo = f"{calidad_tag} {categoria} {marca} {producto}"
                
                precio_raw = str(item.get('precio_final', '0'))
                try:
                    precio_str = precio_raw.replace('$', '').replace('.', '').replace(',', '.').strip()
                    precio_limpio = float(precio_str)
                except ValueError:
                    continue 
                    
                if precio_limpio <= 0:
                    continue
                    
                producto_db = {
                    "client_id": "proveedor_one_services", 
                    "nombre_consolidado": nombre_completo,
                    "precio": precio_limpio,
                    "stock": 99
                }
                lote_total.append(producto_db)
                
        except Exception as e:
            print(f"🚨 Error en la extracción de página {page}: {e}")
            break
            
        page += 1
        time.sleep(1)

    if lote_total:
        print(f"\n📦 Extracción completa. {len(lote_total)} repuestos listos para la base de datos.")
        try:
            supabase.table("productos").delete().eq("client_id", "proveedor_one_services").execute()
            supabase.table("productos").insert(lote_total).execute()
            print("✅ Catálogo de One Services subido a Supabase exitosamente.")
        except Exception as e:
            print(f"❌ Error al subir a base de datos: {e}")

if __name__ == "__main__":
    sincronizar_one_services()