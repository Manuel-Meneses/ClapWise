import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage

# Cargar variables de entorno (asumimos que la raíz del proyecto tiene el .env)
load_dotenv()

# Inicialización de clientes (fuera de la función para no recargar en cada llamada)
try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
except Exception as e:
    print(f"❌ Error de inicialización en el Demonio de Maxwell: {str(e)}")

def filtrar_entropia(texto_caotico: str, client_id: str) -> dict:
    """
    Toma un bloque de texto con alta entropía (datos crudos), extrae un catálogo 
    estructurado incluyendo variantes, calcula tensores semánticos y lo inyecta a Supabase.
    """
    print(f"\n[{client_id}] 1. 👁️ El Demonio de Maxwell está analizando el caos y extrayendo variantes...")
    
    # 1. ACTUALIZAMOS LAS INSTRUCCIONES: Agregamos Talles y Colores
    instrucciones = """
    Eres un procesador de datos estricto. Tu trabajo es extraer productos de un texto caótico o código fuente HTML.
    Debes devolver ÚNICAMENTE un array en formato JSON puro.
    Cada objeto debe tener estas claves obligatorias: 
    - "nombre_consolidado" (en minúsculas)
    - "precio" (número entero)
    - "stock" (número entero, asume 1 si no hay dato)
    - "talles" (string, ej: "S, M, L" o "Único")
    - "colores" (string, ej: "Rojo, Negro" o "No especificado")
    No uses formato markdown, solo devuelve el array desde el corchete de apertura hasta el de cierre.
    """
    
    mensajes = [
        SystemMessage(content=instrucciones),
        HumanMessage(content=texto_caotico)
    ]
    
    try:
        respuesta = llm.invoke(mensajes)
        texto_limpio = respuesta.content.strip().replace("```json", "").replace("```", "")
        productos_estructurados = json.loads(texto_limpio)
        print(f"[{client_id}] ✅ Entropía reducida. Se detectaron {len(productos_estructurados)} productos.")
        
    except Exception as e:
        print(f"[{client_id}] ❌ Falla de procesamiento: {str(e)}")
        return {"status": "error", "message": "Error de LLM", "details": str(e)}

    print(f"[{client_id}] 2. 🧬 Calculando tensores enriquecidos e inyectando al núcleo...")
    
    # --- NUEVO BLOQUE DE LIMPIEZA ---
    print(f"[{client_id}] 🧹 Limpiando catálogo viejo para evitar duplicados...")
    try:
        # Esto borra ÚNICAMENTE las filas de este cliente específico
        supabase.table("productos").delete().eq("client_id", client_id).execute()
    except Exception as e:
        print(f"   ⚠️ Nota: El catálogo estaba vacío o hubo un error al limpiar: {str(e)}")
    # ---------------------------------

    productos_inyectados = 0
    
    for p in productos_estructurados: 
        try:
            nombre_base = p.get('nombre_consolidado', 'producto_desconocido')
            precio = p.get('precio', 0)
            stock = p.get('stock', 1)
            talles = p.get('talles', 'Único')
            colores = p.get('colores', 'No especificado')
            
            # 2. ENRIQUECIMIENTO SEMÁNTICO: Colapsamos las variables en un solo estado observable
            nombre_enriquecido = f"{nombre_base} | Talles: {talles} | Colores: {colores}"
            
            print(f"   -> Vectorizando: {nombre_enriquecido} | ${precio} | Stock: {stock}")
            
            # El modelo ahora proyecta todo en 3072 dimensiones
            vector = embeddings_model.embed_query(nombre_enriquecido)
            
            datos_db = {
                "client_id": client_id,
                "nombre_consolidado": nombre_enriquecido,
                "precio": precio,
                "stock": stock,
                "embedding": vector
            }
            
            supabase.table("productos").insert(datos_db).execute()
            productos_inyectados += 1
            
        except Exception as e:
            print(f"   ❌ Error al inyectar: {str(e)}")

    return {"status": "success", "productos_inyectados_exito": productos_inyectados}