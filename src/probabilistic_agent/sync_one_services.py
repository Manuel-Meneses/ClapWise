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
    print("📥 Iniciando extracción y traducción de One Services...\n")
    
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7,es-US;q=0.6",
        "referer": "https://www.one-service.com.ar/index.php",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    cookies = {
        "cf_clearance": "eVQGoj7bbI0shfKoGlnVqw70jrWHjp3BiCF06nD4Q4w-1785440974-1.2.1.1-2s8zwRIcLrnrOR5ik.uMnoLZcqaBuVeTZ66iR67QuVRfEpGiV25gQm5kqb.6h5BpKynMSGgiNAIQhH1OluMxg4Oly1v.5AIJZXpLflU4KcCtBby856rna7Cg3cdwgRyoorJQWWa6p0WlAg5fQ9XP2LL9phm7e5VAzroiK.JvYalEyWeo4mAJb4qoYUKHtj_Bz6uY3m6RIojhQkMeV.2jnF3H85FttLgU6ABIPp2PtyBs8iWUu.Q8Rzj9be_emwIGAAJniMhss73Bs1zSvRLokylDNhhRkvmn6zpuT0uYOsQbeq4bsfZ8Ddi_00ymyCRe20JCDg29QDt_a8dyza3HexHjtju.kwblNjpeO2Go.xI",
        "dncs": "1",
        "trusted_session": "eyJ1aWQiOjI2MDQsImFwaV9rZXkiOiIzYjYyYjc5MTA5NjQzN2JhYjFkMDFkNGNjYmRkNWM1OCJ9"
    }

    page = 1
    total_pages = 1 
    lote_total = []
    
    while page <= total_pages:
        print(f"📄 Procesando página {page} de {total_pages}...")
        url = f"https://www.one-service.com.ar/api/productos.php?_=0.007064804498742805&uid=2604&api=3b62b791096437bab1d01d4ccbdd5c58&dwt=1536&page={page}"
        
        try:
            respuesta = requests.get(url, headers=headers, cookies=cookies)
            if respuesta.status_code != 200:
                print(f"❌ Error HTTP {respuesta.status_code}.")
                break
                
            datos_json = respuesta.json()
            if page == 1:
                total_pages = datos_json.get('total_pages', 1)
                
            productos = datos_json.get('body', [])
            
            for item in productos:
                if not item.get('permite_pedido', False):
                    continue
                    
                categoria = str(item.get('categoria', '')).strip().upper()
                marca = str(item.get('marca', '')).strip().upper()
                producto = str(item.get('producto', '')).strip().upper()
                
                # 🛑 REGLA IPHONE
                if "IPHONE" in marca or "IPHONE" in producto:
                    continue
                
                # 🗑️ EXCLUSIONES (Lo que no se ofrece)
                if any(basura in producto for basura in ["MECANICO", "OLED SMALL", "HD +", "FHD"]):
                    continue
                
                # 🏷️ TRADUCTOR DE CALIDADES (El embudo de Joa)
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

    # --- INYECCIÓN EN SUPABASE ---
    if lote_total:
        print(f"\n📦 Extracción completa. {len(lote_total)} repuestos listos.")
        try:
            supabase.table("productos").delete().eq("client_id", "proveedor_one_services").execute()
            supabase.table("productos").insert(lote_total).execute()
            print("✅ Catálogo de One Services actualizado exitosamente.")
        except Exception as e:
            print(f"❌ Error al subir a base de datos: {e}")

if __name__ == "__main__":
    sincronizar_one_services()