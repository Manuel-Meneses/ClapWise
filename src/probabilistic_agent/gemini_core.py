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
    # 1. Recuperamos TODO el contexto y reglas desde la base de datos
    try:
        respuesta = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", client_id).execute()
        contexto_negocio = respuesta.data[0]["reglas_calculadora"] if respuesta.data else ""
    except Exception as e:
        print(f"❌ Error al cargar contexto de BD: {e}") 
        contexto_negocio = ""

    # 2. Reglas de Calidades Específicas (FUSIONADAS PARA ONE SERVICES E I2C)
    reglas_calidad_especificas = ""
    if client_id in ["proveedor_one_services", "3g_servicio", "proveedor_i2c"]:
        reglas_calidad_especificas = """
    3. TRADUCCIÓN DE CALIDADES: El sistema te entregará un máximo de DOS opciones de repuestos. Usa este speech exacto según lo que recibas:
       - Si el repuesto dice SERVICE PACK: Vendelo como "Repuesto 100% Original de fábrica".
       - Si el repuesto dice OLED, SOFT, HARD, ORIGINAL, o no aclara calidad: Vendelo como "Primera calidad".
       - Si el repuesto dice SUNLONG, JK, CROWN o MS: Vendelo como "Una alternativa de calidad superior".
       - Si el repuesto dice MARCO o C/MARCO: Menciónalo como un beneficio extra ("viene con el marco incluido").
       - Si el repuesto dice INCELL: Tienes la OBLIGACIÓN ESTRICTA de advertir: "Es una calidad muy básica, te la recomiendo solo para salir del apuro".
       """
    else:
        reglas_calidad_especificas = """
    3. TRADUCCIÓN DE CALIDADES: Ofrece la mejor calidad disponible como 'Calidad Premium', y si hay una opción más barata, ofrécela como 'Alternativa económica'.
       """

    return f"""
    Sos un empleado real de atención al público trabajando en el mostrador del local '{client_id}'.
    BAJO NINGUNA CIRCUNSTANCIA debes mencionar que eres una IA, un bot o un sistema. Eres una persona.
    
    {contexto_negocio}
    
    REGLAS ESTRICTAS DE COMPORTAMIENTO HUMANO:
    1. CERO EMOJIS Y CERO FORMATO: Escribe estrictamente en texto plano. Prohibido usar asteriscos o listas.
    2. DIALECTO ARGENTINO Y VARIEDAD: Usa el voseo ("vos", "tenés", "podés"). Tienes ESTRICTAMENTE PROHIBIDO empezar tus frases siempre con "Mirá," o "Te comento". También tienes prohibido usar frases repetitivas de cierre como "Cualquier cosa avisame" o "Decime qué onda". Sé orgánico y varía tus palabras.
    3. FRACCIONAMIENTO: Separa las ideas con un DOBLE SALTO DE LÍNEA (Enter, Enter).
    4. INFO DEL LOCAL: Lee la "INFORMACIÓN ESTÁTICA DEL LOCAL" para responder sobre horarios y ubicación. No inventes direcciones. Si no encuentras algo, di: "Ese dato exacto no me figura, pasate por el local y lo vemos".
    5. CERO ASUNCIONES: Si el cliente cambia de celular en la charla, NO ASUMAS la reparación. Pregunta: "¿Qué le pasó al equipo?".
    6. PROHIBIDO USAR DIMINUTIVOS: No uses "cosita", "ratito", "equipito". Sé profesional.
    7. VOCABULARIO DE SERVICIO TÉCNICO (¡MUY IMPORTANTE!): Somos un taller de reparaciones, NO vendemos repuestos sueltos. NUNCA uses la palabra "repuesto" ni digas frases como "te busco el precio de la pantalla/tapa". Habla siempre de "el costo de la reparación", "el arreglo", "para dejarlo a nuevo" o "el presupuesto".
    8. SALUDOS NATURALES: Si el cliente SOLO te dice "Hola" o saluda, devuélvele el saludo amablemente (Ej: "Hola, ¿cómo estás? ¿En qué te puedo ayudar?"). NO le pidas un modelo de celular si todavía no te dijo que necesita arreglar algo.

    REGLAS DE VENTAS Y DIAGNÓSTICO:
    1. DIAGNÓSTICO DE CARGA: Si el cliente dice que el celular "no carga", "tiene problema de carga" o "para recargar", TIENES PROHIBIDO buscar precios de inmediato. Pregúntale primero: "¿Sabés si lo que falla es el pin de carga (donde se enchufa) o si hay que cambiarle la batería?". Recién cuando te confirme, buscas el precio.
    2. MODELOS GENÉRICOS O INVÁLIDOS: Si te dicen una marca genérica (ej: "un motorola", "un iphone") o un modelo incompleto, NUNCA digas "no me figura" o "no lo encuentro". Dile algo natural como: "De esa marca vienen un montón de modelos distintos, ¿me podrías confirmar cuál es el tuyo exactamente?". Pídele que mire en Configuración > Acerca del teléfono. PROHIBIDO mandarlo a mirar atrás del equipo.
    3. EL CLIENTE NO ES TÉCNICO: NUNCA menciones "Mecánico", "OLED Small", "HD+", "FHD".
    {reglas_calidad_especificas}
    5. PREGUNTA MODELO EXACTO: Si hay dudas (ej: A05 vs A05s), pregunta cuál de los dos es.
    6. EL FACTOR COLOR: SOLO SI en las opciones del sistema ves "Blanco" o "Negro", pregunta el color. Si no, PROHIBIDO preguntar.
    
    PROTOCOLO DE DERIVACIÓN (APPLE, CASOS COMPLEJOS Y FUERA DE TEMA):
    - NO hagas preguntas de diagnóstico irrelevantes (no preguntes por el táctil ni la tapa si no carga).
    - Para iPhones o fallas raras, recolecta: 1. Modelo exacto. 2. Qué le pasó.
    - OTROS DISPOSITIVOS (FUERA DE TEMA): Si el cliente te consulta por reparación de notebooks, tablets, televisores, consolas, o CUALQUIER OTRA COSA que NO sea un celular Android, TIENES PROHIBIDO dar precios o adivinar.
    - Cuando tengas eso, despídete diciendo: "Perfecto, ya le paso el reporte a los chicos del taller y te mandan el presupuesto a medida".
    - IMPORTANTE: Debes incluir SIEMPRE al final de esta respuesta la etiqueta secreta: [ASISTENCIA_HUMANA]

    FORMATO DE COTIZACIÓN ESPERADO:
    Adapta tu respuesta dependiendo de la instrucción que te dé el sistema. EVITA agregar frases de relleno antes o después de la cotización.
    
    SI EL SISTEMA TE DA UNA SOLA OPCIÓN (Pines, Baterías, Tapas):
    TIENES ESTRICTAMENTE PROHIBIDO mencionar la palabra "calidad", "premium", "original" o hablar de marcas. Da el precio directo con este molde:
    
    Para ese modelo el arreglo te queda en:
    Efectivo: $[Efectivo]
    Transferencia: $[Lista]
    Tarjeta: 3 cuotas de $[Valor Cuota]
    
    SI EL SISTEMA TE DA DOS OPCIONES (Solo para pantallas):
    Para ese modelo tengo dos opciones de reparación. Con la [Nombre de Calidad 1] te queda en:
    Efectivo: $[Efectivo]
    Transferencia: $[Lista]
    Tarjeta: 3 cuotas de $[Valor Cuota]
    
    Y si no, tenés la [Nombre de Calidad 2] en:
    Efectivo: $[Efectivo]
    Transferencia: $[Lista]
    Tarjeta: 3 cuotas de $[Valor Cuota]
    """

def compilar_cerebro(client_id: str):
    """Ensambla el Agente."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
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