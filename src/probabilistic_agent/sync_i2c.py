import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# =========================================================
# LÓGICA DE NEGOCIO Y CLASIFICACIÓN DE i2c
# =========================================================

def clasificar_calidad_i2c(titulo_producto):
    """
    Clasifica las calidades de los módulos (pantallas) según las reglas de i2c.
    """
    titulo = titulo_producto.upper()
    
    if "SERVICE PACK" in titulo:
        return "SERVICE PACK"
    elif "CROWN" in titulo or " MS" in titulo or "MS " in titulo:
        return "CROWN/MS"
    elif "INCELL" in titulo:
        return "INCELL"
    else:
        # Cualquier otra cosa (OLED, ORIGINAL, CON MARCO o vacío) cae como OLED
        return "OLED"

def es_placa_de_carga_valida(titulo_producto):
    """
    Filtra los productos de carga:
    Nos interesan: "Placa", "Plaquita", "Flex de carga".
    DESCARTAMOS: "Pin de carga" (sueltos).
    """
    titulo = titulo_producto.upper()
    if " PIN " in f" {titulo} ":
        return False
    if "PLACA" in titulo or "FLEX" in titulo:
        return True
    return False

def extraer_precio_numerico(precio_str):
    """
    Limpia el texto del precio ('$ 15.000,00' -> 15000.0)
    """
    try:
        limpio = re.sub(r'[^\d]', '', precio_str)
        return float(limpio) / 100
    except:
        return 0.0

# =========================================================
# BUSCADOR WEB (SCRAPING DE i2c) - VERSIÓN CORREGIDA
# =========================================================
def quitar_tildes(texto):
    """
    Quita los acentos de un texto para que las comparaciones no fallen.
    'Módulo' -> 'Modulo'
    """
    try:
        texto = str(texto)
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    except:
        return texto

def buscar_en_i2c(modelo_cliente: str, tipo_repuesto: str):
    """
    Busca en i2c usando la técnica de extraer textos de etiquetas <a>,
    con soporte para tildes y caracteres especiales.
    """
    base_url = "https://www.i2cmayorista.com"
    resultados = []
    
    busqueda_url = f"{base_url}/search/?q={requests.utils.quote(modelo_cliente)}"
    print(f"🔍 [i2c] Buscando en: {busqueda_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        respuesta = requests.get(busqueda_url, headers=headers, timeout=10)
        
        if respuesta.status_code != 200:
            print(f"❌ [i2c] Error de conexión: {respuesta.status_code}")
            return resultados
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        etiquetas_a = soup.find_all('a')
        
        for etiqueta in etiquetas_a:
            texto_crudo = etiqueta.get_text(separator="|", strip=True)
            
            # ELIMINAMOS el: if "$" not in texto_crudo: continue
                
            partes = texto_crudo.split("|")
            titulo_original = partes[0].strip() 
            
            precio_texto = "0"
            for parte in partes:
                # Limpiamos puntos y comas para ver si es un número puro
                parte_limpia = parte.replace('.', '').replace(',', '').strip()
                
                # Si tiene el $ o si es un número largo (ej: 04320)
                if "$" in parte or (parte_limpia.isdigit() and len(parte_limpia) >= 4):
                    precio_texto = parte
                    break
                    
            precio_num = extraer_precio_numerico(precio_texto)
            
            # Ahora sí, si el precio extraído es inválido o 0, lo descartamos
            if precio_num <= 0:
                continue

            titulo_limpio = quitar_tildes(titulo_original).upper()
            
            # 🔥 NUEVO FILTRO ESTRICTO (El mismo que usamos en Supabase)
            # Limpiamos el título de la web y lo separamos por palabras
            nombre_pad = f" {titulo_limpio.replace('/', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ')} "
            modelo_limpio_arr = modelo_cliente.upper().split()
            coincide_todo = True
            
            for t in modelo_limpio_arr:
                t_str = str(t).strip()
                if not t_str: continue
                variantes_termino = [t_str]
                
                # Expansión inteligente (ej: J6 -> J06, G5 -> G05)
                if len(t_str) == 2 and t_str[0].isalpha() and t_str[1].isdigit():
                    variantes_termino.append(f"{t_str[0]}0{t_str[1]}") 
                elif len(t_str) == 3 and t_str[0].isalpha() and t_str[1] == '0' and t_str[2].isdigit():
                    variantes_termino.append(f"{t_str[0]}{t_str[2]}") 
                    
                encontrado = False
                for variante in variantes_termino:
                    if f" {variante} " in nombre_pad:
                        encontrado = True
                        break 
                        
                if not encontrado:
                    coincide_todo = False
                    break
                    
            # MAGIA: Si la web devolvió un producto que NO ES el modelo pedido (Ej: J6 Plus), se salta y se ignora.
            if not coincide_todo:
                continue

            # === SI PASÓ EL CONTROL DE ADUANA, RECIÉN ACÁ LO CLASIFICAMOS ===
            if tipo_repuesto == "pantalla":
                # 🚫 FILTRO ASESINO PARA I2C (IGNORAR MECÁNICOS)
                if "MECANICO" in titulo_limpio and not any(buena in titulo_limpio for buena in ["CROWN", "PREMIUM", "OLED"]):
                    continue
                    
                # Ahora "MODULO" va a atrapar tanto a "Modulo" como a "Módulo"
                if "MODULO" in titulo_limpio or "PANTALLA" in titulo_limpio:
                    calidad = clasificar_calidad_i2c(titulo_original) # Pasamos el original para mantener "CROWN", etc.
                    resultados.append({
                        "proveedor": "i2c",
                        "producto": f"Pantalla {calidad}",
                        "precio_costo": precio_num
                    })
                    
            elif tipo_repuesto == "bateria":
                if "BATERIA" in titulo_limpio:
                    resultados.append({
                        "proveedor": "i2c",
                        "producto": "Batería",
                        "precio_costo": precio_num
                    })
                    
            elif tipo_repuesto == "placa_carga":
                # Le pasamos el limpio por si dice "Plaquíta" (raro, pero posible)
                if es_placa_de_carga_valida(titulo_limpio):
                    resultados.append({
                        "proveedor": "i2c",
                        "producto": "Placa de Carga",
                        "precio_costo": precio_num
                    })
                    
            elif tipo_repuesto == "camara":
                if "LENTE" in titulo_limpio or "CAMARA" in titulo_limpio:
                    resultados.append({
                        "proveedor": "i2c",
                        "producto": "Lente de Cámara",
                        "precio_costo": precio_num
                    })
                    
    except Exception as e:
        print(f"🚨 [i2c] Error en el scraping: {e}")
        
    return resultados
    
# =========================================================
# PRUEBA RÁPIDA DE LA LÓGICA FINAL
# =========================================================
if __name__ == "__main__":
    print("Probando lógica final con pantallas Moto G22...")
    resultados_pantalla = buscar_en_i2c("Moto G22", "pantalla")
    for r in resultados_pantalla:
        print(r)
        
    print("\nProbando lógica final con placas de A12...")
    resultados_placa = buscar_en_i2c("A12", "placa_carga")
    for r in resultados_placa:
        print(r)