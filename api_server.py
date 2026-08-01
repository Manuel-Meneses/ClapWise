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
    print("🔄 Forzando sincronización inicial al encender el servidor...")
    sincronizar_calculadora()
    sincronizar_one_services()
    
    # Mantenemos solo a One Services y la Calculadora
    scheduler.add_job(sincronizar_one_services, 'interval', hours=6)
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
API_TOKEN = "kCxB6tsn2E4qyf6P53EfSvqg" 

# ========================================================
# 🚀 FUNCIONES DE ENVÍO Y CONTROL HACIA CHATWOOT
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

# 👇 NUEVA FUNCIÓN: Cambia el estado de la charla para notificar a Joa
def cambiar_estado_chatwoot(conversation_id: str, status: str = "open"):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/toggle_status"
    
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "status": status
    }
    
    try:
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            print(f"🔔 ¡ASISTENCIA HUMANA ACTIVADA! Conversación {conversation_id} pasada a '{status}'.")
        else:
            print(f"❌ Error cambiando estado en Chatwoot: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción cambiando estado en Chatwoot: {e}")

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
        
        config_memoria = {"configurable": {"thread_id": str(sender_id)}}
        resultado = agente.invoke({"messages": historial}, config=config_memoria)
        
        contenido = resultado["messages"][-1].content
        
        if isinstance(contenido, list):
            textos = []
            for item in contenido:
                if isinstance(item, dict) and "text" in item:
                    textos.append(item["text"])
                elif isinstance(item, str):
                    textos.append(item)
            respuesta_final = "".join(textos)
        else:
            respuesta_final = str(contenido)
        
        # 👇 NUEVA LÓGICA DE INTERCEPCIÓN (DERIVACIÓN A HUMANO)
        if "[ASISTENCIA_HUMANA]" in respuesta_final:
            print(f"⚠️ El Bot solicitó derivar la conversación {conversation_id} a un humano.")
            
            # 1. Limpiamos la etiqueta para que el cliente no vea códigos raros
            respuesta_limpia = respuesta_final.replace("[ASISTENCIA_HUMANA]", "").strip()
            
            # 2. Le mandamos el mensaje final al cliente
            enviar_mensaje_chatwoot(conversation_id, respuesta_limpia)
            
            # 3. Le pasamos la pelota a Joa abriendo la conversación en la bandeja
            cambiar_estado_chatwoot(conversation_id, status="open")
        else:
            # Si no pide ayuda, responde y sigue normal
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
                
                # Despachamos la tarea (podés usar background_tasks si ves que Chatwoot hace timeout)
                procesar_y_responder_fondo(texto_cliente, sender_id, conversation_id)
                
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 Error leyendo Webhook de Chatwoot: {traceback.format_exc()}")
        return {"status": "error"}