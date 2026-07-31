import os
import asyncio
import requests as req
from fastapi import FastAPI, Request, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage

# Importaciones de tu IA (Asegurate de que las rutas coincidan con tu proyecto)
from src.probabilistic_agent.sync_excel import sincronizar_calculadora
from src.probabilistic_agent.sync_one_services import sincronizar_one_services
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras

# ========================================================
# ⚙️ CONFIGURACIÓN DEL RELOJ AUTOMÁTICO
# ========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏰ Iniciando el reloj de automatización...")
    scheduler = BackgroundScheduler()
    
    # Mantenemos solo a One Services y la Calculadora
    scheduler.add_job(sincronizar_one_services, 'interval', hours=24)
    scheduler.add_job(sincronizar_calculadora, 'interval', hours=12) 
    
    scheduler.start()
    yield
    print("🛑 Apagando el reloj de automatización...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# ========================================================
# 🔑 CREDENCIALES DE CHATWOOT (Completá estos datos)
# ========================================================
CHATWOOT_URL = "https://chatwoot-production-eaad.up.railway.app"
ACCOUNT_ID = "1" 

# 👇 Reemplazá esto por el "Token de Acceso" de los Ajustes de Perfil
API_TOKEN = "zioujKf9UvXiDYbjmyTwBt4V" 

# ========================================================
# 🚀 FUNCIÓN DE ENVÍO (De Render hacia Chatwoot)
# ========================================================
def enviar_mensaje_chatwoot(conversation_id: str, texto_respuesta: str):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "content": texto_respuesta,
        "message_type": "outgoing",
        "private": False # Si está en False, el cliente lo lee. True es nota interna.
    }
    
    try:
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            print(f"✅ Respuesta de IA inyectada en Chatwoot (Conv: {conversation_id}).")
        else:
            print(f"❌ Error enviando a Chatwoot: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción enviando a Chatwoot: {e}")

# ========================================================
# 🧠 TAREA DE FONDO (Procesa con Gemini y responde)
# ========================================================
def procesar_y_responder_fondo(texto_cliente: str, sender_id: str, conversation_id: str):
    print(f"🧠 La IA está pensando la respuesta para {sender_id}...")
    
    try:
        agente = compilar_cerebro(sender_id)
        instrucciones = obtener_instrucciones_seguras(sender_id)
        
        historial = [
            SystemMessage(content=instrucciones),
            HumanMessage(content=texto_cliente)
        ]
        
        # Ejecutamos el agente de LangGraph
        resultado = agente.invoke({"messages": historial})
        respuesta_final = resultado["messages"][-1].content
        
        # Le enviamos la respuesta a Chatwoot en lugar de a Meta
        enviar_mensaje_chatwoot(conversation_id, respuesta_final)
        
    except Exception as e:
        import traceback
        print(f"🚨 Error crítico en el agente: {traceback.format_exc()}")

# ========================================================
# 📩 RECEPCIÓN DE MENSAJES (De Chatwoot hacia Render)
# ========================================================
@app.post("/webhook/chatwoot")
async def recibir_mensaje_chatwoot(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    
    try:
        # Solo procesamos si es un mensaje nuevo entrante (del cliente, no nuestro)
        if body.get("event") == "message_created" and body.get("message_type") == "incoming":
            
            texto_cliente = body.get("content", "")
            conversation_id = str(body.get("conversation", {}).get("id", ""))
            sender_id = str(body.get("sender", {}).get("id", ""))
            
            if texto_cliente and conversation_id:
                print(f"\n📩 [Chatwoot Webhook] Mensaje de {sender_id}: {texto_cliente}")
                
                # Despachamos la tarea en segundo plano para no bloquear a Chatwoot
                ## background_tasks.add_task(procesar_y_responder_fondo, texto_cliente, sender_id, conversation_id)
                procesar_y_responder_fondo(texto_cliente, sender_id, conversation_id)
                
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 Error leyendo Webhook de Chatwoot: {traceback.format_exc()}")
        return {"status": "error"}