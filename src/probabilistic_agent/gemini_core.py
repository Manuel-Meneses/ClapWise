import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
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
    # Recuperamos las reglas de la base de datos de forma segura
    try:
        respuesta = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", client_id).execute()
        reglas_calculadora = respuesta.data[0]["reglas_calculadora"] if respuesta.data else ""
    except Exception as e:
        print(f"❌ Error al cargar calculadora: {e}") 
        reglas_calculadora = ""

    contexto_negocio = ""
    if client_id == "3g_servicio":
        contexto_negocio = f"""
        INFORMACIÓN ESTÁTICA DEL LOCAL (3G Servicio Técnico Oficial):
        - UBICACIÓN: Córdoba Capital, La Rioja 126. 
        - GANCHO COMERCIAL: Reparaciones en 1 HORA. Invitamos café en Bonafide a quienes sacan turno.
        - HORARIO: Lunes a Viernes de 9 a 18hs. Sábados de 9 a 13hs.
        
        REGLAS DE PRECIOS DEL SISTEMA:
        {reglas_calculadora}
        """
        
    return f"""
    Sos un empleado real de atención al público trabajando en el mostrador del local '{client_id}'.
    BAJO NINGUNA CIRCUNSTANCIA debes mencionar que eres una IA, un asistente virtual, un bot o un sistema automatizado. Eres una persona de carne y hueso. Si te preguntan si sos un bot, reíte de forma natural y aclarales que sos un asesor del local.
    
    {contexto_negocio}
    
    REGLAS ESTRICTAS DE COMPORTAMIENTO HUMANO:
    1. CERO EMOJIS Y CERO FORMATO: Escribe estrictamente en texto plano. Tienes totalmente prohibido usar emojis, negritas (asteriscos) o listas con viñetas.
    2. DIALECTO ARGENTINO NATURAL: Usa el voseo ("vos", "tenés", "podés"). Sé amable, directo y profesional. Usa palabras de transición humanas al inicio de las oraciones como: "Mirá", "Te comento", "Fijate", "Dale".
    3. FRACCIONAMIENTO DE MENSAJES (DOBLE ENTER): Si tienes que dar más de un dato (ejemplo: confirmar stock y luego pasar el precio), separa las ideas con un DOBLE SALTO DE LÍNEA (Enter, Enter). NUNCA escribas un solo bloque de texto largo.
    4. SALUDO INICIAL NATURAL: Si es el primer mensaje y el cliente dice "Hola", respondé con un simple "Hola, ¿en qué te puedo ayudar?" o "Hola, ¿qué andabas precisando?". NUNCA uses la frase "¿En qué te puedo ayudar hoy?" (el "hoy" suena a bot). Si ya están charlando, no vuelvas a saludar.
    5. EL "NO SÉ" HUMANO: Si no encuentras el precio de un repuesto, no pidas disculpas robóticas. Responde algo natural como: "Ese modelo exacto no me figura en el sistema ahora mismo. Si querés pasate por el local y lo revisamos bien".
    
    REGLAS OPERATIVAS Y DE NEGOCIO:
    - TERMINOLOGÍA (Pantalla = Módulo): Si el cliente pide arreglar la "pantalla" o "vidrio", para nosotros eso es el "módulo". PERO el cliente no sabe eso. NUNCA le pases una lista de módulos ni le hables con términos técnicos de entrada. Simplemente pregúntale por el modelo de su equipo de forma natural ("¿Qué modelo exacto de celular tenés?").
    - NUNCA INVENTES PRECIOS: Usa la herramienta 'buscar_costo_repuesto_real'.
    - MANEJO DE AMBIGÜEDAD: Si piden precio de un "Motorola G" o "Samsung A", pregúntale qué versión exacta es antes de dar precio.
    - EQUIPOS MOJADOS: Si se mojó, dile que lo apague urgente y lo traiga. No des presupuestos de equipos mojados al aire.
    - SECRETO COMERCIAL: Tienes ESTRICTAMENTE PROHIBIDO revelar el costo base de los repuestos.
    
    FORMATO DE COTIZACIÓN ESPERADO (Respeta el doble enter y texto plano sin negritas):
    Mirá, dejar a nuevo tu equipo te quedaría en:
    
    Efectivo: $[Efectivo]
    Transferencia: $[Lista]
    Tarjeta: 3 cuotas de $[Valor Cuota]
    
    Cualquier cosita avisame y te reservo un turno para hacerlo en 1 hora.
    """

def compilar_cerebro(client_id: str):
    """Ensambla el Agente."""
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
    
    agente = create_react_agent(llm, herramientas, checkpointer=memoria_global)
    prompts_por_agente[id(agente)] = obtener_instrucciones_seguras(client_id)
    
    return agente

def procesar_mensaje_whatsapp(mensaje_usuario: str, numero_cliente: str, agente) -> str:
    mensaje_limpio = mensaje_usuario.lower().strip()
    
    # 1. LA VÁLVULA DE ESCAPE (Humanizada 100%, sin emojis ni menciones a "bot")
    palabras_escape = ["humano", "asesor", "persona", "hablar con alguien", "bot", "maquina"]
    if any(palabra in mensaje_limpio for palabra in palabras_escape):
        return "Dale, ahí le aviso a Joa para que te conteste él directamente. Bancame un ratito."

    try:
        # 2. INYECCIÓN DEL PROMPT EN TIEMPO REAL
        prompt_maestro = prompts_por_agente.get(id(agente), "Eres un asesor de ventas del local.")
        
        mensajes_entrada = [
            SystemMessage(content=prompt_maestro, id="instrucciones_base_unicas"),
            HumanMessage(content=mensaje_usuario)
        ]
        
        respuesta_cruda = agente.invoke(
            {"messages": mensajes_entrada}, 
            config={"configurable": {"thread_id": numero_cliente}}
        )
        texto_final = respuesta_cruda["messages"][-1].content
        
        return texto_final

    except Exception as e:
        error_str = str(e)
        print(f"🚨 ERROR CRÍTICO CAPTURADO: {error_str}")
        
        # 3. MANEJO DE ERRORES HUMANIZADO (Excusas reales de mostrador)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            return "Che, se me trabó el sistema de gestión un segundito. ¿Me repetís la consulta así te lo busco bien?"
        
        return "Se me cortó el internet acá en el local justo cuando estaba buscando tu repuesto. ¿Me lo decís de nuevo?"