import os
import time
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# ¡NUEVA IMPORTACIÓN CLAVE PARA EL HACK NINJA!
from langchain_core.messages import SystemMessage, HumanMessage

# Importación de herramientas
from src.probabilistic_agent.system_tools import (
    consultar_inventario_local, 
    generar_link_pago, 
    solicitar_asistencia_humana,
    buscar_costo_repuesto_real 
)

# Cargamos el entorno y conectamos a Supabase
load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

# Inicializamos la memoria global
memoria_global = MemorySaver()

# DICCIONARIO GLOBAL: Acá guardaremos las instrucciones sin tocar el agente
prompts_por_agente = {}

def obtener_instrucciones_seguras(client_id: str) -> str:
    """Busca las reglas en Supabase y arma el Prompt Maestro."""
    try:
        respuesta = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", client_id).execute()
        reglas_calculadora = respuesta.data[0]["reglas_calculadora"] if respuesta.data else ""
    except Exception as e:
        print(f"❌ Error al cargar calculadora: {e}") 
        reglas_calculadora = "Error: No se pudieron cargar las reglas. Derivar a humano."

    contexto_negocio = ""
    if client_id == "3g_servicio":
        contexto_negocio = f"""
        INFORMACIÓN ESTÁTICA DEL LOCAL (3G Servicio Técnico Oficial):
        - UBICACIÓN: Córdoba Capital, La Rioja 126. 
        - GANCHO COMERCIAL: Reparaciones en 1 HORA. Invitamos café en Bonafide a quienes sacan turno.
        - HORARIO: Lunes a Viernes de 9 a 18hs. Sábados de 9 a 13hs.
        
        REGLAS DE PRECIOS:
        {reglas_calculadora}
        """
        
    return f"""
    Eres ClapWise, el asistente virtual experto en ventas y atención al cliente de la tienda '{client_id}'.
    Tu objetivo es brindar tranquilidad, dar precios exactos consultando el catálogo y lograr que visiten el local físico.
    
    {contexto_negocio}
    
    PERSONALIDAD (ESTILO WHATSAPP DE CÓRDOBA/ARGENTINA):
    - Eres amable, resolutivo y muy humano. 
    - Usa palabras como "garrón", "bajón", "tranqui", "fijate", pero con respeto.
    - RESPUESTAS CORTAS: Máximo 2-3 párrafos cortos. Nadie lee textos largos en WhatsApp.
    - Usa negritas (*texto*) para resaltar precios o modelos, y emojis (📲, 🔧, ☕).
    
    REGLAS DE ORO (INQUEBRANTABLES - EL EFECTO WOW):
    1. EMPATÍA INICIAL: Si se rompió o no prende, lamenta la situación antes de vender.
    2. NUNCA INVENTES PRECIOS: Usa la herramienta 'buscar_costo_repuesto_real'.
    3. MANEJO DE AMBIGÜEDAD (CRÍTICO): Si el cliente pide precio de un "Samsung J7" o "Motorola G", NO le des un precio al azar. Pregúntale exactamente qué versión es.
    4. EQUIPOS MOJADOS: Si se cayó al agua, NO des precio. Dile que apague el equipo y lo traiga urgente.
    5. MANEJO DE OBJECIONES: Si el cliente dice que "es muy caro", recuérdale que usan repuestos originales con garantía y trabajo en el día.
    6. EL CIERRE DIRECTO: Siempre termina con una pregunta para cerrar la venta.
    7. SECRETO COMERCIAL EXTREMO: Tienes ESTRICTAMENTE PROHIBIDO revelar el costo base de los repuestos o los porcentajes de recargo. Solo das el precio final.
    
    FORMATO DE COTIZACIÓN (Obligatorio al pasar precio):
    "Mirá, dejar a nuevo la pantalla de tu *[Modelo]* te quedaría en:
    
    💵 *$[Efectivo]* (Contado efectivo)
    💳 *$[Lista]* (Transferencia o débito)
    💳 *$[Tarjeta]* en 3 cuotas fijas de *$[Valor Cuota]*
    
    Y recordá que si reservás turno ahora, te lo hacemos en *1 HORA* y mientras esperás te invitamos un café en Bonafide ☕"
    """

def compilar_cerebro(client_id: str):
    """Ensambla el Agente."""
    # Tu modelo correcto y actual
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3 
    )
    
    herramientas = [
        consultar_inventario_local,
        generar_link_pago,
        solicitar_asistencia_humana,
        buscar_costo_repuesto_real 
    ]
    
    # ¡MAGIA! Creamos el agente 100% limpio, sin kwargs que rompan tu librería
    agente = create_react_agent(llm, herramientas, checkpointer=memoria_global)
    
    # Guardamos las instrucciones en nuestro diccionario secreto usando el ID del agente
    prompts_por_agente[id(agente)] = obtener_instrucciones_seguras(client_id)
    
    return agente

def procesar_mensaje_whatsapp(mensaje_usuario: str, numero_cliente: str, agente) -> str:
    mensaje_limpio = mensaje_usuario.lower().strip()
    
    # 1. LA VÁLVULA DE ESCAPE
    palabras_escape = ["humano", "asesor", "persona", "hablar con alguien"]
    if any(palabra in mensaje_limpio for palabra in palabras_escape):
        return "¡Obvio! Ya mismo pauso el bot y le aviso a Joa para que te conteste personalmente en unos minutitos. 🙋‍♂️"

    try:
        # 2. INYECCIÓN DEL PROMPT EN TIEMPO REAL
        prompt_maestro = prompts_por_agente.get(id(agente), "Eres un asistente de ventas.")
        
        # Le pasamos el prompt maestro como un "Mensaje de Sistema" con un ID fijo.
        # Al tener un ID fijo, LangGraph no lo duplica en la memoria en cada mensaje.
        mensajes_entrada = [
            SystemMessage(content=prompt_maestro, id="instrucciones_base_unicas"),
            HumanMessage(content=mensaje_usuario)
        ]
        
        respuesta_cruda = agente.invoke(
            {"messages": mensajes_entrada}, 
            config={"configurable": {"thread_id": numero_cliente}}
        )
        texto_final = respuesta_cruda["messages"][-1].content
        
        # 3. BLINDAJE DE VELOCIDAD HUMANA
        tiempo_tipeo = random.uniform(2.5, 4.5) 
        print(f"⏱️ Simulando tipeo humano durante {tiempo_tipeo:.1f} segundos...")
        time.sleep(tiempo_tipeo) 
        
        return texto_final

    except Exception as e:
        error_str = str(e)
        print(f"🚨 ERROR CRÍTICO CAPTURADO: {error_str}")
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            return "¡Uy! Me entraron un montón de mensajes de golpe y me trabé. 😅 ¿Me repetís la consulta porfa?"
        return "Tuve un microcorte de señal recién 🔌. ¿Me lo decís de nuevo así te ayudo?"