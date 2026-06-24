import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Conectar a la Capa A (Base de datos)
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# Conectar a la Capa B (Motor de Embeddings)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

print("Iniciando vectorización del inventario...")

# 1. Obtener los productos que no tienen vector
respuesta = supabase.table("productos").select("id_producto, nombre_consolidado").is_("embedding", "null").execute()
productos = respuesta.data

if not productos:
    print("Todos los productos ya están vectorizados.")
else:
    for prod in productos:
        print(f"Calculando tensor para: {prod['nombre_consolidado']}")
        # Generar el vector de 768 dimensiones
        vector = embeddings_model.embed_query(prod['nombre_consolidado'])
        
        # Actualizar el producto en Supabase
        supabase.table("productos").update({"embedding": vector}).eq("id_producto", prod['id_producto']).execute()
        
    print("✅ Vectorización completada. El espacio HNSW está calibrado.")