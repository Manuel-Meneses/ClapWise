import os
import random
import asyncio
import requests as req
from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage

# Importaciones de tus módulos
from src.probabilistic_agent.sync_excel import sincronizar_calculadora
from src.probabilistic_agent.sync_proveedores import sincronizar_proveedores_adicionales
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras

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

app = FastAPI(title="Motor ClapWise API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MensajeWhatsApp(BaseModel):
    client_id: str
    numero_telefono: str 
    texto: str

agentes_activos = {}

def obtener_agente(client_id: str):
    if client_id not in agentes_activos:
        agentes_activos[client_id] = compilar_cerebro(client_id)
    return agentes_activos[client_id]

# ========================================================
# 👇 EL PORTERO DE META (GET - Verifica la URL)
# ========================================================
@app.get("/webhook/chat")
async def verificar_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    TOKEN_VERIFICACION = "clapwise_secreto"
    
    if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFICACION:
        print("✅ Webhook verificado correctamente por Meta.")
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Error de verificación de token")


# ========================================================
# 🧠 PROCESAMIENTO EN SEGUNDO PLANO (Asíncrono y fraccionado)
# ========================================================
async def procesar_y_responder_fondo(texto_cliente: str, numero_cliente: str):
    try:
        print(f"🧠 IA pensando respuesta para {numero_cliente}...")
        client_id = "3g_servicio"
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
        
        # Usamos ainvoke directo, que es súper rápido y no bloquea el servidor
        respuesta = await agente.ainvoke(entradas, config=configuracion)
        
        contenido = respuesta['messages'][-1].content
        texto_limpio = contenido[0]['text'] if isinstance(contenido, list) else contenido
        
        print(f"🔪 Fraccionando mensaje...")
        
        # Cortamos el texto por cada doble enter
        fragmentos = [f.strip() for f in texto_limpio.split('\n\n') if f.strip()]
        
        # Enviamos con retraso humano
        for i, fragmento in enumerate(fragmentos):
            if i == 0:
                tiempo_espera = random.uniform(20.0, 30.0) # El primer mensaje tarda más (leyendo)
            else:
                tiempo_espera = random.uniform(8.0, 10.0) # Los siguientes salen rápido (tipeando)
                
            print(f"⏳ Tipeando fragmento {i+1}... esperando {tiempo_espera:.1f} segs")
            await asyncio.sleep(tiempo_espera)
            enviar_mensaje_whatsapp(numero_cliente, fragmento)
            
        print("✅ Toda la secuencia fue enviada.")
        
    except Exception as e:
        import traceback
        print(f"🚨 ERROR EN TAREA DE FONDO: {traceback.format_exc()}")


# ========================================================
# 📩 RECEPCIÓN DE MENSAJES (POST - Lo que escucha a Meta)
# ========================================================
@app.post("/webhook/chat")
async def recibir_mensaje(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    
    try:
        if "entry" in body and "changes" in body["entry"][0]:
            cambios = body["entry"][0]["changes"][0]["value"]
            
            if "messages" in cambios:
                mensaje_meta = cambios["messages"][0]
                numero_cliente = mensaje_meta["from"]
                texto_cliente = mensaje_meta["text"]["body"]
                
                print(f"📩 Nuevo mensaje de {numero_cliente}: {texto_cliente}")
                
                # MAGIA: Delegamos a la tarea de fondo y liberamos el webhook
                background_tasks.add_task(procesar_y_responder_fondo, texto_cliente, numero_cliente)
                
        # Le devolvemos un OK a Meta en 0.1 segundos para que no tire error de Timeout
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 ERROR EN WEBHOOK: {traceback.format_exc()}")
        return {"status": "error"}


# ========================================================
# 🚀 ENVÍO DE MENSAJES A META
# ========================================================
def enviar_mensaje_whatsapp(numero_destino, texto_respuesta):
    TOKEN = "EAATkL1hn6uEBSMlVD9wREiuZCZAiWmJj1GIqvSGLMZAk6IS1YsvWHgXGkTs7km75wbMSiLLXfRCBiTrBWcOWZB4RJFZAo16KXwtN7cGOJCkCPNDrfwJRbr8awTkhKVH3bhr0KFUuy4NMh9muWNY0yHIzwANScFxPV1yCZC9g6fcZBvpKnKT10rQmuF9R8x26SphigZDZD"
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
        print("✅ Mensaje entregado a Meta.")
    else:
        print(f"❌ Error al enviar mensaje: {respuesta.text}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Reactor FastAPI ClapWise...")
    uvicorn.run(app, host="0.0.0.0", port=8000)