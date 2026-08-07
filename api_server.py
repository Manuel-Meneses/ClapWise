import os
import time
import asyncio
import requests as req
from fastapi import FastAPI, Request, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage

# Importaciones de tu IA
from src.probabilistic_agent.sync_excel import sincronizar_calculadora
from src.probabilistic_agent.sync_one_services import sincronizar_one_services
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras

# ========================================================
# 🧠 MEMORIA RAM DE PAUSAS Y CONTROL
# ========================================================
# Guarda IDs de conversación donde el bot está apagado. Ej: {"12345": True}
conversaciones_pausadas = {}

# Guarda los últimos mensajes que mandó el bot para no auto-pausarse
mensajes_enviados_por_bot = []

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
def enviar_mensaje_chatwoot(conversation_id: str, texto_respuesta: str, es_privado: bool = False):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "content": texto_respuesta,
        "message_type": "outgoing",
        "private": es_privado # Si es True, es una nota amarilla solo para Joa
    }
    
    # 🔥 ANOTAMOS EL MENSAJE EN LA MEMORIA PARA NO AUTO-PAUSARNOS
    if not es_privado:
        mensajes_enviados_por_bot.append(texto_respuesta.strip())
        if len(mensajes_enviados_por_bot) > 50:
            mensajes_enviados_por_bot.pop(0) # Mantenemos la lista cortita
            
    try:
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            tipo = "Privado" if es_privado else "Público"
            print(f"✅ Mensaje {tipo} inyectado en Chatwoot (Conv: {conversation_id}).")
        else:
            print(f"❌ Error enviando a Chatwoot: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción enviando a Chatwoot: {e}")

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
            print(f"🔔 Conversación {conversation_id} pasada a '{status}'.")
        else:
            print(f"❌ Error cambiando estado en Chatwoot: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción cambiando estado en Chatwoot: {e}")

def agregar_etiqueta_chatwoot(conversation_id: str, etiqueta: str):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/labels"
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    data = {"labels": [etiqueta]}
    try:
        req.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"🚨 Error agregando etiqueta: {e}")

def asignar_agente_chatwoot(conversation_id: str, agente_id: int = 1):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/assignments"
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    data = {"assignee_id": agente_id}
    
    try:
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            print(f"👤 Conversación {conversation_id} asignada directamente al agente {agente_id} (Joa).")
        else:
            print(f"❌ Error asignando agente: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción asignando agente: {e}")

# ========================================================
# 🧠 TAREA DE FONDO (Procesa con Gemini y responde)
# ========================================================
def procesar_y_responder_fondo(texto_cliente: str, sender_id: str, conversation_id: str):
    print(f"🧠 Gaspar está pensando la respuesta para {sender_id}...")
    
    try:
        agente = compilar_cerebro(sender_id)
        instrucciones = obtener_instrucciones_seguras("3g_servicio")
        
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
        
        # 👇 LÓGICA DE DERIVACIÓN (Precios Altos, Modelos Raros)
        if "[ASISTENCIA_HUMANA]" in respuesta_final:
            print(f"⚠️ Gaspar solicitó derivar la conversación {conversation_id} a Joa.")
            
            # 1. Limpiamos etiqueta y mandamos mensaje al cliente
            respuesta_limpia = respuesta_final.replace("[ASISTENCIA_HUMANA]", "").strip()
            enviar_mensaje_chatwoot(conversation_id, respuesta_limpia)
            
            # 2. Apagamos el bot automáticamente para esta charla
            conversaciones_pausadas[conversation_id] = True
            
            # 3. Alertas visuales para Joa en Chatwoot
            cambiar_estado_chatwoot(conversation_id, status="open")
            # 🔥 CAMBIO: ETIQUETA DERIVACIÓN BOT
            agregar_etiqueta_chatwoot(conversation_id, "#derivado_bot")
            asignar_agente_chatwoot(conversation_id, agente_id=1) 
            
            enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO: Gaspar derivó esta consulta. Revisá el historial arriba y tomá el control. (Para reactivarlo escribe /activar)", es_privado=True)
            
        else:
            # 🔥 Sistema de múltiples burbujas (Saltos en WhatsApp) 🔥
            print(f"✅ Respuesta normal procesada para {conversation_id}")
            
            # Cortamos la respuesta gigante cada vez que encontremos "||"
            burbujas = respuesta_final.split("||")
            
            for burbuja in burbujas:
                texto_burbuja = burbuja.strip()
                if texto_burbuja:  # Verificamos que no esté vacío
                    enviar_mensaje_chatwoot(conversation_id, texto_burbuja)
                    time.sleep(1.5)  # Pausa de 1.5 segundos entre cada globito

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
        event = body.get("event")
        message_type = body.get("message_type")
        conversation_id = str(body.get("conversation", {}).get("id", ""))
        
        # ----------------------------------------------------
        # 🛡️ VÁLVULA DE SEGURIDAD 1: FILTRO ANTI-GRUPOS DE WHATSAPP
        # ----------------------------------------------------
        sender_phone = str(body.get("sender", {}).get("phone_number", ""))
        sender_identifier = str(body.get("sender", {}).get("identifier", ""))
        
        # Eliminamos el bloqueo por guion ("-") porque Chatwoot usa UUIDs con guiones para clientes normales.
        if "@g.us" in sender_phone or "@g.us" in sender_identifier:
            print(f"🤫 [FILTRO GRUPOS] Mensaje de grupo detectado en la charla {conversation_id}. Ignorando.")
            return {"status": "ok"}
            
        # ----------------------------------------------------
        # 1. CONTROL DE PAUSA MANUAL POR JOA (Notas Privadas)
        # ----------------------------------------------------
        if event == "message_created" and message_type == "outgoing" and body.get("private") == True:
            comando = body.get("content", "").strip().lower()
            
            if comando == "/pausa":
                conversaciones_pausadas[conversation_id] = True
                print(f"🛑 Joa pausó el bot manualmente en la charla {conversation_id}")
                enviar_mensaje_chatwoot(conversation_id, "✅ Bot pausado. Ahora tienes el control total.", es_privado=True)
                return {"status": "ok"}
                
            elif comando == "/activar":
                conversaciones_pausadas.pop(conversation_id, None)
                print(f"▶️ Joa reactivó el bot en la charla {conversation_id}")
                enviar_mensaje_chatwoot(conversation_id, "✅ Bot reactivado. Gaspar responderá el próximo mensaje del cliente.", es_privado=True)
                return {"status": "ok"}

        
        # ----------------------------------------------------
        # 2. AUTO-PAUSA POR USO DE PLANTILLAS Y MACROS (FILTRO NINJA MEJORADO)
        # ----------------------------------------------------
        if event == "message_created" and message_type == "outgoing":
            contenido = body.get("content", "").strip()
            
            # 🔥 CONTROL NINJA MEJORADO: Búsqueda flexible
            fue_gaspar = False
            for msg_guardado in mensajes_enviados_por_bot:
                # Comparamos si una parte del texto coincide (ignora espacios fantasmas de Chatwoot)
                if contenido in msg_guardado or msg_guardado in contenido:
                    fue_gaspar = True
                    mensajes_enviados_por_bot.remove(msg_guardado)
                    break
                    
            if not fue_gaspar:
                # Si definitivamente no fue Gaspar y NO es una nota amarilla... ¡Fue Joa!
                if not body.get("private"):
                    if not conversaciones_pausadas.get(conversation_id):
                        print(f"🤖 Auto-pausa: Joa tomó el control en la charla {conversation_id}")
                        conversaciones_pausadas[conversation_id] = True
                        enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO AUTOMÁTICAMENTE: Detecté que tomaste el control de la charla o enviaste una plantilla. (Para que vuelva el bot escribe /activar)", es_privado=True)
        
        # ----------------------------------------------------
        # 3. PROCESAMIENTO DE MENSAJES DEL CLIENTE
        # ----------------------------------------------------
        if event == "message_created" and message_type == "incoming":
            
            # A) Si el bot está pausado para esta charla, ignoramos el mensaje
            if conversaciones_pausadas.get(conversation_id):
                print(f"🤫 Bot silenciado para charla {conversation_id}. Ignorando mensaje.")
                return {"status": "ok"}
                
            # B) Filtro Anti-Fotos/Audios
            adjuntos = body.get("attachments", [])
            if adjuntos:
                print(f"📸 El cliente envió un archivo en {conversation_id}. Derivando a Joa...")
                conversaciones_pausadas[conversation_id] = True
                enviar_mensaje_chatwoot(conversation_id, "Recibí el archivo. Dame un ratito que se lo paso a los chicos del taller para que lo vean y te digo.")
                cambiar_estado_chatwoot(conversation_id, status="open")
                # 🔥 CAMBIO: ETIQUETA ARCHIVO RECIBIDO
                agregar_etiqueta_chatwoot(conversation_id, "#archivo_recibido")
                asignar_agente_chatwoot(conversation_id, agente_id=1) 
                enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO AUTOMÁTICAMENTE: El cliente envió un archivo.", es_privado=True)
                return {"status": "ok"}
            
            # C) Si es texto normal y el bot NO está pausado, llamamos a Gemini
            texto_cliente = body.get("content", "")
            sender_id = str(body.get("sender", {}).get("id", ""))
            
            if texto_cliente and conversation_id:
                print(f"\n📩 [Chatwoot] Mensaje de {sender_id}: {texto_cliente}")
                background_tasks.add_task(procesar_y_responder_fondo, texto_cliente, sender_id, conversation_id)
                
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 Error leyendo Webhook de Chatwoot: {traceback.format_exc()}")
        return {"status": "error"}