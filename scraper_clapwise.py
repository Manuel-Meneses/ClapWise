from duckduckgo_search import DDGS
import pandas as pd
import time

# 1. Definimos las huellas para encontrar las tiendas
# Apuntamos a Córdoba para aprovechar la cercanía en el mensaje de ventas
query = '"Creado con Tiendanube" "Córdoba"'
resultados = []

print(f"Buscando prospectos para: {query}...\n")

try:
    # 2. Ejecutamos la búsqueda (region='ar-es' prioriza resultados de Argentina)
    with DDGS() as ddgs:
        # max_results controla cuántos links querés extraer
        busqueda = ddgs.text(query, region='ar-es', max_results=150)
        
        for idx, r in enumerate(busqueda):
            titulo = r.get('title', '')
            url = r.get('href', '')
            descripcion = r.get('body', '')
            
            resultados.append({
                "Nombre_Tienda": titulo.replace(" - Creado con Tiendanube", "").strip(),
                "URL": url,
                "Descripcion": descripcion
            })
            print(f"[{idx+1}] Extraído: {url}")
            
            # Un pequeño delay para ser respetuosos con el servidor y evitar bloqueos
            time.sleep(0.5)

except Exception as e:
    print(f"Se produjo un error durante el scraping: {e}")

# 3. Procesamiento y limpieza con Pandas
if resultados:
    df = pd.DataFrame(resultados)
    
    # Eliminamos cualquier tienda duplicada por URL
    df = df.drop_duplicates(subset=['URL'])
    
    # Exportamos la base de datos limpia a un CSV
    nombre_archivo = "prospectos_clapwise_cordoba.csv"
    df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ ¡Scraping finalizado! Se guardaron {len(df)} tiendas únicas en '{nombre_archivo}'.")
    print("Ya podés abrir el CSV y empezar a filtrar para mandar los mensajes.")
else:
    print("\nNo se encontraron resultados. Probá ajustando las palabras clave de la query.")