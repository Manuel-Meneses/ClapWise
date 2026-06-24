import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client() -> Client:
    """Instancia el cliente de la base de datos"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Faltan las credenciales de Supabase en el .env")
        
    return create_client(url, key)

def consultar_stock_exacto(client_id: str, limite_precio: float = None):
    """Consulta ACID pura. Sin vectores todavía para el MVP rápido."""
    supabase = get_supabase_client()
    
    query = supabase.table('productos').select("*").eq('client_id', client_id).gt('stock', 0)
    
    if limite_precio:
        query = query.lte('precio', limite_precio)
        
    respuesta = query.execute()
    return respuesta.data