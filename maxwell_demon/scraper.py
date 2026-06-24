import requests
from bs4 import BeautifulSoup
from maxwell_demon.entropy_filter import filtrar_entropia

def clonar_catalogo_web(url_tienda: str, client_id: str):
    """
    Extrae todo el texto visible de una URL y lo inyecta en el núcleo del sistema.
    """
    print(f"\n🌐 Iniciando clonación de: {url_tienda}")
    
    try:
        # 1. Hacemos la petición a la web simulando ser un navegador normal
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        respuesta = requests.get(url_tienda, headers=headers, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parseamos el HTML y destruimos los scripts y estilos (limpieza de ruido)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        # 3. Extraemos solo el texto puro
        texto_crudo = soup.get_text(separator=' ', strip=True)
        
        # Cortamos un límite de caracteres para no saturar al LLM (aprox 30.000 caracteres)
        texto_seguro = texto_crudo[:30000]
        print(f"📦 Se extrajeron {len(texto_seguro)} caracteres de entropía pura.")
        
        # 4. Pasamos el caos por el filtro que ya construimos
        resultado = filtrar_entropia(texto_seguro, client_id)
        
        if resultado["status"] == "success":
            print(f"✅ ¡Clonación exitosa para {client_id}! Catálogo listo en Supabase.")
        else:
            print("❌ El Demonio no pudo procesar los datos.")
            
    except Exception as e:
        print(f"❌ Error al intentar acceder a la web: {str(e)}")

if __name__ == "__main__":
    # Aquí configuras tu lista de los 10 clientes para que se ejecute en cadena
    clientes_objetivo = [
        {"id": "damelosiempre", "url": "https://www.damelosiempre.com.ar/productos"},
        {"id": "tussyoff", "url": "https://tussy.com.ar/ropa"},
        {"id": "baesics", "url": "https://baesics.ar/collections/all"},
        {"id": "blunder", "url": "https://blunder.com.ar/drop-el-dia-arranca"},
        {"id": "tussyoff", "url": "https://tussy.com.ar/ropa"},
    ]
    
    for cliente in clientes_objetivo:
        clonar_catalogo_web(cliente["url"], cliente["id"])