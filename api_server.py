from datetime import datetime, timedelta, timezone
import os
import time
import asyncio
import requests as req
from fastapi import FastAPI, Request, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Importaciones de tu IA
from src.probabilistic_agent.sync_excel import sincronizar_calculadora
from src.probabilistic_agent.sync_one_services import sincronizar_one_services
from src.probabilistic_agent.gemini_core import compilar_cerebro, obtener_instrucciones_seguras
from src.probabilistic_agent.sync_mundo_parts import sincronizar_mundo_parts 

# ========================================================
# 🧠 MEMORIA RAM DE PAUSAS Y CONTROL
# ========================================================
# Guarda IDs de conversación donde el bot está apagado. Ej: {"12345": True}
conversaciones_pausadas = {}

# Guarda los últimos mensajes que mandó el bot para no auto-pausarse
mensajes_enviados_por_bot = []

# Guarda las sesiones a las que ya se les curó la amnesia
sesiones_hidratadas = set()

mensajes_buffer = {}
temporizadores_buffer = {}

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
    sincronizar_mundo_parts()
    
    scheduler.add_job(sincronizar_one_services, 'interval', hours=6)
    scheduler.add_job(sincronizar_calculadora, 'interval', hours=6) 
    scheduler.add_job(sincronizar_mundo_parts, 'interval', hours=6)
    
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
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            print(f"🏷️ Etiqueta '{etiqueta}' agregada con éxito a la charla {conversation_id}.")
        else:
            print(f"❌ CHATWOOT RECHAZÓ LA ETIQUETA '{etiqueta}': {respuesta.text}")
    except Exception as e:
        print(f"🚨 Error de conexión agregando etiqueta: {e}")

def asignar_agente_chatwoot(conversation_id: str, agente_id: int = 0):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/assignments"
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    data = {"assignee_id": agente_id}
    
    try:
        respuesta = req.post(url, headers=headers, json=data)
        if respuesta.status_code == 200:
            if agente_id == 0:
                print(f"👤 Conversación {conversation_id} enviada a bandeja 'Sin Asignar' (Todos los agentes).")
            else:
                print(f"👤 Conversación {conversation_id} asignada directamente al agente {agente_id}.")
        else:
            print(f"❌ Error asignando agente: {respuesta.text}")
    except Exception as e:
        print(f"🚨 Excepción asignando agente: {e}")

def recuperar_historial_chatwoot(conversation_id: str):
    """Va a buscar los últimos mensajes a Chatwoot, los formatea para LangChain
       y les INYECTA LA FECHA Y HORA para que la IA no pierda la noción del tiempo."""
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": API_TOKEN,
        "Content-Type": "application/json"
    }
    historial_lc = []
    
    try:
        respuesta = req.get(url, headers=headers)
        if respuesta.status_code == 200:
            mensajes = respuesta.json().get("payload", [])
            
            # Invertimos para que queden en orden cronológico, tomando solo los últimos 10
            for msg in reversed(mensajes[:10]):
                es_privado = msg.get("private", False)
                tipo = msg.get("message_type")
                contenido = msg.get("content")
                
                # 🔥 TRUCO DEL TIEMPO: Extraemos el timestamp de Chatwoot
                timestamp_unix = msg.get("created_at")
                fecha_hora_texto = ""
                
                if timestamp_unix:
                    # Convertimos el número de Chatwoot a una hora legible de Argentina (UTC-3)
                    dt = datetime.fromtimestamp(timestamp_unix, timezone.utc) - timedelta(hours=3)
                    fecha_hora_texto = f" [Enviado el {dt.strftime('%d/%m a las %H:%M')}]"
                
                if contenido and not es_privado:
                    if tipo == 0:  # Cliente
                        # Le pegamos la fecha y hora al final del texto del cliente
                        historial_lc.append(HumanMessage(content=f"{contenido}{fecha_hora_texto}"))
                    elif tipo == 1:  # Bot o Joa
                        # Evitamos que el bot lea sus propias alertas de sistema o derivaciones
                        if "🛑" not in contenido and "[ASISTENCIA_HUMANA]" not in contenido:
                            # Le pegamos la fecha y hora al final del texto del bot/Joa
                            historial_lc.append(AIMessage(content=f"{contenido}{fecha_hora_texto}"))
    except Exception as e:
        print(f"🚨 Error recuperando memoria de Chatwoot: {e}")
        
    return historial_lc

# ========================================================
# 🧠 TAREA DE FONDO (Procesa con Gemini y responde)
# ========================================================
def procesar_y_responder_fondo(texto_cliente: str, sender_id: str, conversation_id: str, usuario_meta: str = "", red_social: str = ""):
    print(f"🧠 Gaspar está pensando la respuesta...")
    
    try:
        agente = compilar_cerebro(sender_id)
        instrucciones = obtener_instrucciones_seguras("3g_servicio")
        
        historial = [SystemMessage(content=instrucciones)]
        
        # Inyectamos el historial completo de Chatwoot si es la primera interacción tras el reinicio
        if conversation_id not in sesiones_hidratadas:
            print(f"🔄 Inyectando historial de Chatwoot para la charla {conversation_id}...")
            mensajes_viejos = recuperar_historial_chatwoot(conversation_id)
            
            if mensajes_viejos and isinstance(mensajes_viejos[-1], HumanMessage) and mensajes_viejos[-1].content.strip() == texto_cliente.strip():
                mensajes_viejos.pop()
                
            historial.extend(mensajes_viejos)
            sesiones_hidratadas.add(conversation_id)
            print("✅ Historial inyectado con éxito.")
            
        if usuario_meta:
            nota_oculta = f"\n\n(Nota del sistema: El cliente te escribe desde {red_social} y su usuario es @{usuario_meta}. Asegurate de agregar este @usuario en la descripción del evento al agendar el turno)."
            texto_cliente = texto_cliente + nota_oculta
            
        historial.append(HumanMessage(content=texto_cliente))
        
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
        
        if "[ASISTENCIA_HUMANA]" in respuesta_final:
            print(f"⚠️ Gaspar solicitó derivar la conversación {conversation_id} a Joa.")
            respuesta_limpia = respuesta_final.replace("[ASISTENCIA_HUMANA]", "").strip()
            enviar_mensaje_chatwoot(conversation_id, respuesta_limpia)
            conversaciones_pausadas[conversation_id] = True
            cambiar_estado_chatwoot(conversation_id, status="open")
            agregar_etiqueta_chatwoot(conversation_id, "derivado_bot")
            asignar_agente_chatwoot(conversation_id, agente_id=0) 
            enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO: Gaspar derivó esta consulta. Revisá el historial arriba y tomá el control. (Para reactivarlo escribe /activar)", es_privado=True)
            
        else:
            print(f"✅ Respuesta normal procesada para {conversation_id}")
            burbujas = respuesta_final.split("||")
            for burbuja in burbujas:
                texto_burbuja = burbuja.strip()
                if texto_burbuja:
                    enviar_mensaje_chatwoot(conversation_id, texto_burbuja)
                    time.sleep(4)

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
        
        sender_phone = str(body.get("sender", {}).get("phone_number", ""))
        sender_identifier = str(body.get("sender", {}).get("identifier", ""))
        
        if "@g.us" in sender_phone or "@g.us" in sender_identifier:
            return {"status": "ok"}
            
        if event == "message_created" and message_type == "outgoing" and body.get("private") == True:
            comando = body.get("content", "").strip().lower()
            if comando == "/pausa":
                conversaciones_pausadas[conversation_id] = True
                enviar_mensaje_chatwoot(conversation_id, "✅ Bot pausado. Ahora tienes el control total.", es_privado=True)
                return {"status": "ok"}
            elif comando == "/activar":
                conversaciones_pausadas.pop(conversation_id, None)
                enviar_mensaje_chatwoot(conversation_id, "✅ Bot reactivado. Gaspar responderá el próximo mensaje del cliente.", es_privado=True)
                return {"status": "ok"}

        if event == "message_created" and message_type == "outgoing":
            contenido = body.get("content", "").strip()
            fue_gaspar = False
            for msg_guardado in mensajes_enviados_por_bot:
                if contenido in msg_guardado or msg_guardado in contenido:
                    fue_gaspar = True
                    mensajes_enviados_por_bot.remove(msg_guardado)
                    break
            if not fue_gaspar:
                if not body.get("private"):
                    if not conversaciones_pausadas.get(conversation_id):
                        conversaciones_pausadas[conversation_id] = True
                        enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO AUTOMÁTICAMENTE: Detecté que tomaste el control de la charla o enviaste una plantilla. (Para que vuelva el bot escribe /activar)", es_privado=True)
        
        if event == "message_created" and message_type == "incoming":
            if conversaciones_pausadas.get(conversation_id):
                return {"status": "ok"}
                
            adjuntos = body.get("attachments", [])
            if adjuntos:
                conversaciones_pausadas[conversation_id] = True
                enviar_mensaje_chatwoot(conversation_id, "Recibí el archivo. Dame un ratito que se lo paso a los chicos del taller para que lo vean y te digo.")
                cambiar_estado_chatwoot(conversation_id, status="open")
                agregar_etiqueta_chatwoot(conversation_id, "archivo_recibido")
                asignar_agente_chatwoot(conversation_id, agente_id=0) 
                enviar_mensaje_chatwoot(conversation_id, "🛑 BOT PAUSADO AUTOMÁTICAMENTE: El cliente envió un archivo.", es_privado=True)
                return {"status": "ok"}
            
            # ----------------------------------------------------
            # 🔥 SALA DE ESPERA (7 SEGS) + SUSURRO ANTI-CONFUSIÓN
            # ----------------------------------------------------
            texto_cliente = body.get("content", "")
            sender_id = str(body.get("sender", {}).get("id", ""))
            
            atributos = body.get("sender", {}).get("additional_attributes", {})
            usuario_meta = atributos.get("username") or atributos.get("screen_name") or ""
            red_social = body.get("inbox", {}).get("name", "Chat")
            
            if texto_cliente and conversation_id:
                print(f"\n📩 [Chatwoot] Mensaje retenido en sala de espera: {texto_cliente}")
                
                # 1. Calculamos cuánto tiempo pasó desde la última charla
                ahora = datetime.now()
                ultima_vez = ultima_interaccion.get(conversation_id)
                
                nota_tiempo = ""
                if ultima_vez and (ahora - ultima_vez > timedelta(hours=2)):
                    print(f"🕒 Pasaron más de 2 horas. Preparando susurro de contexto para {conversation_id}.")
                    nota_tiempo = "\n\n(Nota oculta del sistema: Inicia un nuevo día o sesión. Responde SOLO a lo que el cliente pregunte ahora. Tienes PROHIBIDO mencionar proactivamente presupuestos o faltas de stock de celulares que se hablaron ayer o hace horas, a menos que el cliente te pregunte por ellos de nuevo.)\n\n"
                
                # Actualizamos el reloj
                ultima_interaccion[conversation_id] = ahora
                
                # Si llega un nuevo mensaje del mismo cliente rápido, reiniciamos el reloj de 7 segs
                if conversation_id in temporizadores_buffer:
                    temporizadores_buffer[conversation_id].cancel()
                    
                if conversation_id in mensajes_buffer:
                    mensajes_buffer[conversation_id].append(texto_cliente)
                else:
                    mensajes_buffer[conversation_id] = [texto_cliente]
                    
                async def esperar_y_procesar(conv_id, s_id, u_meta, r_social, susurro):
                    try:
                        # ⏳ Espera 7 segundos a que el cliente termine de tipear todo
                        await asyncio.sleep(7) 
                        
                        textos = mensajes_buffer.pop(conv_id, [])
                        if textos:
                            mensaje_unido = "\n".join(textos)
                            
                            # Si es el primer mensaje después de mucho tiempo, le pegamos el susurro al principio
                            if susurro:
                                mensaje_unido = susurro + mensaje_unido
                                
                            print(f"📦 Paquete completo enviado a Gaspar: '{mensaje_unido}'")
                            
                            await asyncio.to_thread(procesar_y_responder_fondo, mensaje_unido, s_id, conv_id, u_meta, r_social)
                    except asyncio.CancelledError:
                        pass # Entró otro mensaje antes de los 7s, se cancela esta tarea y la nueva toma el control
                        
                task = asyncio.create_task(esperar_y_procesar(conversation_id, sender_id, usuario_meta, red_social, nota_tiempo))
                temporizadores_buffer[conversation_id] = task
                
        return {"status": "ok"}
        
    except Exception as e:
        import traceback
        print(f"🚨 Error leyendo Webhook de Chatwoot: {traceback.format_exc()}")
        return {"status": "error"} 