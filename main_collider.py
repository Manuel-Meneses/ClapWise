from langchain_core.messages import SystemMessage, HumanMessage
from src.probabilistic_agent.gemini_core import compilar_cerebro

def iniciar_simulacion_ventas(client_id: str):
    print(f"--- Iniciando Sistema ClapWise para: {client_id} ---")
    
    # 1. Llamamos a la fábrica del núcleo probabilístico
    agente = compilar_cerebro(client_id)
    
    # 2. Definimos las leyes de la termodinámica del bot
    instrucciones = f"""
    Eres ClapWise, el mejor asistente de ventas de WhatsApp.
    El ID de esta tienda es '{client_id}'.
    Regla de Oro: NUNCA inventes precios ni stock.
    DEBES usar la herramienta 'consultar_inventario_local' para responder.
    Sé empático, breve y usa tono cordobés (ej: "che", "mirá").
    """
    
    print("Bot encendido. Escribe 'salir' para apagar el sistema.")
    
    # 3. El bucle de interacción humana
    while True:
        mensaje_usuario = input("\n👤 Cliente: ")
        if mensaje_usuario.lower() == 'salir':
            print("Apagando el sistema...")
            break
            
        entradas = {
            "messages": [
                SystemMessage(content=instrucciones),
                HumanMessage(content=mensaje_usuario)
            ]
        }
        
        try:
            respuesta = agente.invoke(entradas)
            contenido = respuesta['messages'][-1].content
            texto_limpio = contenido[0]['text'] if isinstance(contenido, list) else contenido
            print(f"\n🤖 ClapWise: {texto_limpio}")
        except Exception as e:
            print(f"\n❌ Error de ejecución: {str(e)}")

if __name__ == "__main__":
    CLIENTE_PRUEBA = "cliente_001_showroom"
    iniciar_simulacion_ventas(CLIENTE_PRUEBA)