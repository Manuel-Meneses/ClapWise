import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar entorno de forma segura
load_dotenv()

# Singleton inverso: Inicializamos el cliente una sola vez para ahorrar memoria
_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Faltan credenciales de Supabase en el .env")
        _supabase_client = create_client(url, key)
    return _supabase_client

def buscar_productos_similares(query_vector: list, client_id: str, threshold: float = 0.1, limit: int = 3) -> list:
    """
    Ejecuta el cálculo matemático de distancia exacta (Fuerza Bruta) en el núcleo relacional.
    """
    try:
        supabase = get_supabase_client()
        respuesta = supabase.rpc(
            "buscar_similitud_semantica",
            {
                "query_embedding": query_vector,
                "p_client_id": client_id,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        return respuesta.data
    except Exception as e:
        print(f"❌ Error en la Capa SQL: {str(e)}")
        return []