import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

try:
    print("1. Probando generador de vectores de Google...")
    vector = embeddings_model.embed_query("ropa para el frío extremo")
    print(f"✅ Tensor generado. Dimensiones: {len(vector)}")
    
    print("2. Cruzando el puente hacia Supabase HNSW...")
    respuesta = supabase.rpc(
        "buscar_similitud_semantica",
        {
            "query_embedding": vector,
            "p_client_id": "cliente_001_showroom",
            "match_threshold": 0.5,
            "match_count": 3
        }
    ).execute()
    
    print("✅ Búsqueda semántica exitosa. Resultados devueltos:")
    print(respuesta.data)
    
except Exception as e:
    print(f"\n❌ Falla detectada en la Capa Semántica: {str(e)}")