from fastapi import FastAPI, HTTPException, Query, Request
import requests as req
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from src.probabilistic_agent.sync_excel import sincronizar_calculadora
from src.probabilistic_agent.sync_proveedores import sincronizar_proveedores_adicionales
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏰ Iniciando el reloj de automatización...")
    scheduler = BackgroundScheduler()
    
    # Cada 12 horas actualiza los proveedores
    scheduler.add_job(sincronizar_proveedores_adicionales, 'interval', hours=12)
    
    # Cada 12 horas actualiza la calculadora de Joa
    scheduler.add_job(sincronizar_calculadora, 'interval', hours=12) 
    
    scheduler.start()
    yield
    print("🛑 Apagando el reloj de automatización...")
    scheduler.shutdown()

# Creamos la función que maneja los ciclos de vida del servidor (Lifespan)
# Instanciamos el framework asíncrono
app = FastAPI(title="Motor ClapWise API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier web se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definimos la estructura de datos que esperamos recibir
class MensajeWhatsApp(BaseModel):
    client_id: str
    numero_telefono: str # Usaremos esto como el thread_id para la memoria
    texto: str

# Diccionario para almacenar los agentes compilados en memoria por cada cliente
agentes_activos = {}

def obtener_agente(client_id: str):
    if client_id not in agentes_activos:
        agentes_activos[client_id] = compilar_cerebro(client_id)
    return agentes_activos[client_id]


# ========================================================
# 👇 EL PORTERO DE META (Obligatorio para verificar webhook)
# ========================================================
@app.get("/webhook/chat")
async def verificar_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    # Este es el token que tenés que poner en la página de Meta
    TOKEN_VERIFICACION = "clapwise_secreto"
    
    if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFICACION:
        print("✅ Webhook verificado correctamente por Meta.")
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Error de verificación de token")


# ========================================================
@app.post("/webhook/chat")
async def recibir_mensaje(request: Request):
    # 1. Capturamos el formato extraño que manda Meta
    body = await request.json()
    
    try:
        # Extraemos la información navegando por el JSON de Meta
        if "entry" in body and "changes" in body["entry"][0]:
            cambios = body["entry"][0]["changes"][0]["value"]
            
            # Verificamos que sea un mensaje y no una notificación de "leído"
            if "messages" in cambios:
                mensaje_meta = cambios["messages"][0]
                numero_cliente = mensaje_meta["from"]
                texto_cliente = mensaje_meta["text"]["body"]
                
                print(f"📩 Mensaje recibido de {numero_cliente}: {texto_cliente}")
                
                # 2. Procesamos con Gemini
                client_id = "3g_servicio" # Por ahora lo dejamos fijo para tu demo
                agente = obtener_agente(client_id)
                instrucciones = obtener_instrucciones_seguras(client_id)
                
                texto_blindado = f"<mensaje_usuario>{texto_cliente}</mensaje_usuario>"
                entradas = {
                    "messages": [
                        SystemMessage(content=instrucciones),
                        HumanMessage(content=texto_blindado)
                    ]
                }
                
                configuracion = {"configurable": {"thread_id": numero_cliente}}
                respuesta = await agente.ainvoke(entradas, config=configuracion)
                
                contenido = respuesta['messages'][-1].content
                texto_limpio = contenido[0]['text'] if isinstance(contenido, list) else contenido
                
                print(f"🧠 IA calculó la respuesta. Enviando a Meta...")
                
                # 3. Disparamos la respuesta de vuelta al WhatsApp del cliente
                enviar_mensaje_whatsapp(numero_cliente, texto_limpio)
                
        # Siempre hay que devolverle un 200 OK a Meta para que no reintente
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 ERROR: {traceback.format_exc()}")
        return {"status": "error"}

def enviar_mensaje_whatsapp(numero_destino, texto_respuesta):
    # 👇 PEGÁ ACÁ TU TOKEN LARGUÍSIMO DE META
    TOKEN = "EAATkL1hn6uEBSMlVD9wREiuZCZAiWmJj1GIqvSGLMZAk6IS1YsvWHgXGkTs7km75wbMSiLLXfRCBiTrBWcOWZB4RJFZAo16KXwtN7cGOJCkCPNDrfwJRbr8awTkhKVH3bhr0KFUuy4NMh9muWNY0yHIzwANScFxPV1yCZC9g6fcZBvpKnKT10rQmuF9R8x26SphigZDZD"
    # Este es el ID de tu número de prueba que me pasaste arriba
    PHONE_ID = "1271041542753450" 
    
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto_respuesta}
    }
    
    respuesta = req.post(url, headers=headers, json=data)
    
    if respuesta.status_code == 200:
        print("✅ Mensaje entregado exitosamente por WhatsApp.")
    else:
        print(f"❌ Error al enviar mensaje: {respuesta.text}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Reactor FastAPI ClapWise...")
    uvicorn.run(app, host="0.0.0.0", port=8000)