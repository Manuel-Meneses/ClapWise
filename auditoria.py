import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

print("Auditando el núcleo de Supabase...\n")
try:
    respuesta = supabase.table("productos").select("nombre_consolidado, stock, embedding").execute()
    productos = respuesta.data
    
    print(f"📦 Total de productos encontrados: {len(productos)}")
    
    for p in productos:
        # Verificamos si la columna embedding tiene datos o está vacía
        estado_vector = "✅ VECTORIZADO" if p.get('embedding') else "❌ Ciego (SIN VECTOR)"
        print(f"- {p['nombre_consolidado']} (Stock: {p['stock']}) -> {estado_vector}")
        
except Exception as e:
    print(f"❌ Error al consultar la base de datos: {str(e)}")