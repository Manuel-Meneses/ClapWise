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
    estructurado, calcula tensores semánticos de 3072 dimensiones y lo inyecta a Supabase.
    
    Retorna: Diccionario con el estado final de la operación.
    """
    print(f"\n[{client_id}] 1. 👁️ El Demonio de Maxwell está analizando el caos...")
    
    instrucciones = """
    Eres un procesador de datos estricto. Tu trabajo es extraer productos, precios y stock de un texto caótico.
    Debes devolver ÚNICAMENTE un array en formato JSON puro con las claves: "nombre_consolidado" (en minúsculas), "precio" (número entero), "stock" (número entero).
    Si no se menciona stock, asume 1. Si no hay precio, descarta el producto.
    No uses formato markdown, no uses la palabra json, solo devuelve el array desde el corchete de apertura hasta el de cierre.
    """
    
    mensajes = [
        SystemMessage(content=instrucciones),
        HumanMessage(content=texto_caotico)
    ]
    
    # 1. Fase de Extracción (LangChain puro, sin LangGraph)
    try:
        respuesta = llm.invoke(mensajes)
        texto_limpio = respuesta.content.strip().replace("```json", "").replace("```", "")
        productos_estructurados = json.loads(texto_limpio)
        print(f"[{client_id}] ✅ Entropía reducida. Se detectaron {len(productos_estructurados)} productos.")
        
    except json.JSONDecodeError:
        print(f"[{client_id}] ❌ Falla estructural: El LLM no devolvió un JSON válido.")
        return {"status": "error", "message": "JSON inválido", "details": respuesta.content}
    except Exception as e:
        print(f"[{client_id}] ❌ Falla de procesamiento: {str(e)}")
        return {"status": "error", "message": "Error de LLM", "details": str(e)}

    # 2. Fase de Vectorización e Inyección
    print(f"[{client_id}] 2. 🧬 Calculando tensores e inyectando al núcleo de Supabase...")
    productos_inyectados = 0
    
    for p in productos_estructurados:
        try:
            nombre = p.get('nombre_consolidado', 'producto_desconocido')
            precio = p.get('precio', 0)
            stock = p.get('stock', 1)
            
            print(f"   -> Vectorizando: {nombre} | ${precio} | Stock: {stock}")
            
            # Cálculo matemático de la distancia (3072 dimensiones)
            vector = embeddings_model.embed_query(nombre)
            
            datos_db = {
                "client_id": client_id,
                "nombre_consolidado": nombre,
                "precio": precio,
                "stock": stock,
                "embedding": vector
            }
            
            # Inyección a la base de datos
            supabase.table("productos").insert(datos_db).execute()
            productos_inyectados += 1
            
        except Exception as e:
            print(f"   ❌ Error al inyectar el producto '{nombre}': {str(e)}")

    print(f"[{client_id}] 🎉 Proceso completado. {productos_inyectados} inyectados con éxito.")
    
    # 3. Retorno del reporte final
    return {
        "status": "success",
        "productos_extraidos_total": len(productos_estructurados),
        "productos_inyectados_exito": productos_inyectados
    }