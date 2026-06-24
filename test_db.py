import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Probando conexión a: {url}")

try:
    supabase = create_client(url, key)
    respuesta = supabase.table('productos').select("*").execute()
    print(f"✅ Conexión exitosa. Se encontraron {len(respuesta.data)} productos en la base de datos.")
    print(respuesta.data)
except Exception as e:
    print(f"❌ Error crítico en Supabase: {str(e)}")