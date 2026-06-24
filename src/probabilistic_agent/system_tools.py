import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

@tool
def consultar_inventario_local(client_id: str, busqueda_cliente: str) -> str:
    """
    Busca productos en el inventario basándose en el significado de lo que pide el client.
    Ejemplo: Si el cliente busca 'ropa para el frío', esta herramienta buscará similitudes semánticas.
    """
    try:
        # 1. Convertir la búsqueda del cliente en un vector
        query_vector = embeddings_model.embed_query(busqueda_cliente)
        
        # 2. Ejecutar la función matemática en Supabase (buscamos coincidencias con similitud > 0.5)
        respuesta = supabase.rpc(
            "buscar_similitud_semantica",
            {
                "query_embedding": query_vector,
                "p_client_id": client_id,
                "match_threshold": 0.1, 
                "match_count": 3
            }
        ).execute()
        
        resultados = respuesta.data
        
        if not resultados:
            return "No se encontraron productos relacionados con esa búsqueda."
            
        # 3. Formatear la respuesta determinista para el agente
        texto_resultado = "Resultados encontrados en la base de datos:\n"
        for item in resultados:
            texto_resultado += f"- {item['nombre_consolidado'].title()}: Precio ${item['precio']}, Stock: {item['stock']} unidades (Similitud: {item['similitud']:.2f})\n"
            
        return texto_resultado
        
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"

@tool
def generar_link_pago(client_id: str, monto: float, descripcion_producto: str) -> str:
    """
    ÚSALO SOLO CUANDO EL CLIENTE CONFIRME LA COMPRA.
    Genera un enlace de pago (simulado para el MVP) para cobrar el producto.
    """
    # Aquí en el futuro conectarás la API de MercadoPago o similar
    link_simulado = f"https://pagos.clapwise.com/{client_id}/checkout?monto={monto}"
    return f"Link de pago generado con éxito: {link_simulado}. Dile al cliente que puede pagar ahí."

@tool
def solicitar_asistencia_humana(client_id: str, numero_cliente: str, motivo: str) -> str:
    """
    ÚSALO CUANDO EL CLIENTE PIDA HABLAR CON UNA PERSONA O HAGA PREGUNTAS QUE NO PUEDES RESPONDER.
    Notifica al dueño del local para que intervenga en el chat.
    """
    # Aquí en el futuro conectarás una alerta de WhatsApp, Slack o Mail para el dueño
    print(f"🚨 ALERTA HUMANA [{client_id}]: El cliente {numero_cliente} necesita ayuda. Motivo: {motivo}")
    return "Notificación enviada. Dile al cliente que un asesor humano se contactará a la brevedad."