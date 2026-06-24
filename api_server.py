from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras
from fastapi.middleware.cors import CORSMiddleware

# Instanciamos el framework asíncrono
app = FastAPI(title="Motor ClapWise API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier web se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definimos la estructura de datos que esperamos recibir (Webhooks de Meta)
class MensajeWhatsApp(BaseModel):
    client_id: str
    numero_telefono: str # Usaremos esto como el thread_id para la memoria
    texto: str

# Diccionario para almacenar los agentes compilados en memoria por cada cliente
# Así no recompilamos el cerebro en cada mensaje
agentes_activos = {}

def obtener_agente(client_id: str):
    if client_id not in agentes_activos:
        agentes_activos[client_id] = compilar_cerebro(client_id)
    return agentes_activos[client_id]

@app.post("/webhook/chat")
async def recibir_mensaje(datos: MensajeWhatsApp):
    """
    Endpoint principal. Recibe el mensaje, busca la memoria del número de teléfono,
    ejecuta el agente y devuelve la respuesta.
    """
    agente = obtener_agente(datos.client_id)
    instrucciones = obtener_instrucciones_seguras(datos.client_id)
    
    # Empaquetamos el mensaje con el blindaje XML anti-jailbreak
    texto_blindado = f"<mensaje_usuario>{datos.texto}</mensaje_usuario>"
    
    entradas = {
        "messages": [
            SystemMessage(content=instrucciones),
            HumanMessage(content=texto_blindado)
        ]
    }
    
    # Configuramos el hilo de memoria usando el número de teléfono
    configuracion = {"configurable": {"thread_id": datos.numero_telefono}}
    
    try:
        # Usamos ainoke para ejecución asíncrona
        respuesta = await agente.ainvoke(entradas, config=configuracion)
        
        # Extraemos la respuesta final de la IA
        contenido = respuesta['messages'][-1].content
        texto_limpio = contenido[0]['text'] if isinstance(contenido, list) else contenido
        
        return {"status": "success", "respuesta_bot": texto_limpio}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Levantamos el servidor en el puerto 8000
    print("🚀 Iniciando Reactor FastAPI ClapWise...")
    uvicorn.run(app, host="0.0.0.0", port=8000)