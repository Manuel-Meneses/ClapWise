import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool
import requests as req
import json
from src.probabilistic_agent.sync_i2c import buscar_en_i2c

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

@tool
def consultar_inventario_local(client_id: str, busqueda_cliente: str) -> str:
    """Busca productos locales de Joa."""
    try:
        # ATENCIÓN AL CAMBIO: eq("cliente_id", client_id)
        respuesta = supabase.table("productos").select("nombre_consolidado, precio").eq("client_id", client_id).execute()
        resultados = respuesta.data
        if not resultados:
            return "No se encontraron productos en el inventario local."
            
        texto_resultado = "Resultados:\n"
        for item in resultados:
            texto_resultado += f"- {item['nombre_consolidado']}: ${item['precio']}\n"
        return texto_resultado
    except Exception as e:
        return f"Error al consultar: {str(e)}"

@tool
def generar_link_pago(client_id: str, monto: float, descripcion_producto: str) -> str:
    """Genera link de pago."""
    return f"Link de pago: https://pagos.clapwise.com/{client_id}/checkout?monto={monto}"

@tool
def solicitar_asistencia_humana(client_id: str, numero_cliente: str, motivo: str) -> str:
    """Usa esta herramienta para alertar a un humano (Joa). En el campo 'motivo', debes escribir el resumen detallado de la encuesta o problema del cliente."""
    
    print(f"🚨 ALERTANDO A JOA: El cliente {numero_cliente} necesita ayuda. Resumen del bot: {motivo}")
    
    # Los mismos datos de Meta que usamos en tu api_server.py
    TOKEN = "EAATkL1hn6uEBSMlVD9wREiuZCZAiWmJj1GIqvSGLMZAk6IS1YsvWHgXGkTs7km75wbMSiLLXfRCBiTrBWcOWZB4RJFZAo16KXwtN7cGOJCkCPNDrfwJRbr8awTkhKVH3bhr0KFUuy4NMh9muWNY0yHIzwANScFxPV1yCZC9g6fcZBvpKnKT10rQmuF9R8x26SphigZDZD"
    PHONE_ID = "1271041542753450" 
    
    # 👇 ACÁ PONÉS EL CELULAR PERSONAL DE JOA (Con código de país, ej: 549351XXXXXXX)
    NUMERO_DE_JOA = "5493510000000" 
    
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Armamos el mensaje que le va a llegar al celular de Joa
    mensaje_para_joa = f"⚠️ *NUEVO CLIENTE DERIVADO* ⚠️\n\nEl bot acaba de pausarse para este número:\n📞 *{numero_cliente}*\n\n*📋 Resumen de la encuesta (Hecho por la IA):*\n{motivo}\n\nYa podés entrar a la bandeja de entrada para contestarle el presupuesto."
    
    data = {
        "messaging_product": "whatsapp",
        "to": NUMERO_DE_JOA,
        "type": "text",
        "text": {"body": mensaje_para_joa}
    }
    
    # Disparamos el mensaje a Joa
    req.post(url, headers=headers, json=data)
    
    # Le devolvemos este texto al bot para que sepa que hizo bien su trabajo
    return "Notificación enviada exitosamente a Joa con el resumen del diagnóstico. Ya puedes despedirte del cliente."

@tool
def buscar_costo_repuesto_real(modelo: str, tipo_repuesto: str) -> str:
    """Busca repuestos, aplica la matriz de rentabilidad y devuelve los precios finales al cliente."""
    print(f"\n🔍 [SISTEMA] Buscando: '{modelo}' | Repuesto: '{tipo_repuesto}'")
    
    # 1. 🧠 DICCIONARIO DE SINÓNIMOS PARA REPUESTOS (Soluciona Pin vs Conector)
    tipo_rep = tipo_repuesto.lower().replace('ó', 'o').replace('í', 'i').replace('á', 'a').strip()
    sinonimos_busqueda = [tipo_rep]
    
    # Variable estandarizada para pasarle a i2c después
    tipo_repuesto_estandar = "pantalla" 
    
    if "pantalla" in tipo_rep or "modulo" in tipo_rep or "display" in tipo_rep:
        sinonimos_busqueda = ["modulo", "pantalla", "display"]
        tipo_repuesto_estandar = "pantalla"
    elif "pin" in tipo_rep or "carga" in tipo_rep or "conector" in tipo_rep:
        sinonimos_busqueda = ["pin", "conector", "placa", "flex de carga"]
        tipo_repuesto_estandar = "placa_carga"
    elif "bateria" in tipo_rep or "pila" in tipo_rep:
        sinonimos_busqueda = ["bateria", "bat"]
        tipo_repuesto_estandar = "bateria"
    elif "tapa" in tipo_rep or "trasera" in tipo_rep:
        sinonimos_busqueda = ["tapa", "vidrio trasero"]
        tipo_repuesto_estandar = "tapa"
    elif "camara" in tipo_rep or "lente" in tipo_rep:
        sinonimos_busqueda = ["camara", "lente"]
        tipo_repuesto_estandar = "camara"

    PRIORIDAD_PROVEEDORES = ["proveedor_one_services"]

    try:
        # Descargar la matriz de cálculo
        respuesta_matriz = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", "matriz_calculo_interna").execute()
        matriz_raw = respuesta_matriz.data[0]["reglas_calculadora"] if respuesta_matriz.data else "[]"
        matriz = sorted(json.loads(matriz_raw), key=lambda x: x['min'], reverse=True)

        def aplicar_calculadora(costo_base):
            mo, dto, rec = 35000, 0.16, 0.25
            for rango in matriz:
                if costo_base >= rango['min']:
                    mo, dto, rec = rango['mo'], rango['dto'], rango['rec']
                    break
            lista = costo_base + mo
            efectivo = lista * (1 - dto)
            tarjeta = lista * (1 + rec)
            return int(lista), int(efectivo), int(tarjeta), int(tarjeta / 3)

        # 2. 🧠 LIMPIEZA DE MARCAS (Soluciona que el proveedor no escriba "Moto")
        marcas_a_ignorar = ["SAMSUNG", "MOTOROLA", "MOTO", "XIAOMI", "APPLE", "IPHONE", "LG", "NOKIA"]
        modelo_limpio = modelo.upper()
        for marca in marcas_a_ignorar:
            modelo_limpio = modelo_limpio.replace(marca, "")
        modelo_limpio = modelo_limpio.strip()
        if not modelo_limpio: modelo_limpio = modelo.upper()
            
        # 3. 🧠 EXPANSIÓN DE BASE DE DATOS (Soluciona que Supabase esconda el G05)
        variantes_db = [modelo_limpio]
        for t in modelo_limpio.split():
            if len(t) == 2 and t[0].isalpha() and t[1].isdigit():
                variantes_db.append(f"{t[0]}0{t[1]}") # Agrega G05
            elif len(t) == 3 and t[0].isalpha() and t[1] == '0' and t[2].isdigit():
                variantes_db.append(f"{t[0]}{t[2]}") # Agrega G5
                
        # Le decimos a Supabase: Busca G5 "O" G05
        filtro_or = ",".join([f"nombre_consolidado.ilike.%{v}%" for v in variantes_db if v])
        
        repuestos_filtrados = []
       # ---------------------------------------------------------
        # BUSQUEDA 1: BASE DE DATOS (One Services)
        # ---------------------------------------------------------
        for proveedor in PRIORIDAD_PROVEEDORES:
            respuesta = supabase.table("productos").select("*").eq("client_id", proveedor).or_(filtro_or).execute()
            resultados = respuesta.data
            
            if not resultados: continue 
                
            for rep in resultados:
                nombre_bd = str(rep.get('nombre_consolidado', '')).upper()
                
                # REGLA ESTRICTA DE JOA: Bloquear "MARCO" a menos que sea Original
                if "MARCO" in nombre_bd:
                    if not any(palabra in nombre_bd for palabra in ["SERVICE PACK", "ORIG", "ORI"]):
                        continue
                
                texto_bd_lower = nombre_bd.lower().replace('ó', 'o').replace('á', 'a').replace('í', 'i')
                coincide_tipo = any(sin in texto_bd_lower for sin in sinonimos_busqueda)
                
                if coincide_tipo:
                    nombre_limpio_sku = nombre_bd.replace('/', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ')
                    nombre_pad = f" {nombre_limpio_sku} "
                    
                    coincide_todo = True
                    for t in modelo_limpio.split():
                        t_str = str(t).strip()
                        variantes_termino = [t_str]
                        if len(t_str) == 2 and t_str[0].isalpha() and t_str[1].isdigit():
                            variantes_termino.append(f"{t_str[0]}0{t_str[1]}") 
                        elif len(t_str) == 3 and t_str[0].isalpha() and t_str[1] == '0' and t_str[2].isdigit():
                            variantes_termino.append(f"{t_str[0]}{t_str[2]}") 
                            
                        encontrado = False
                        for variante in variantes_termino:
                            if f" {variante} " in nombre_pad:
                                encontrado = True
                                break 
                                
                        if not encontrado:
                            coincide_todo = False
                            break
                    
                    if coincide_todo:
                        repuestos_filtrados.append(rep)

        # ---------------------------------------------------------
        # BUSQUEDA 2: PLAN B (Scraping i2c en tiempo real)
        # ---------------------------------------------------------
        if not repuestos_filtrados:
            print(f"⚠️ Sin stock en One Services. Buscando en i2c...")
            resultados_i2c = buscar_en_i2c(modelo_limpio, tipo_repuesto_estandar)
            
            if resultados_i2c:
                print(f"✅ ¡Repuesto encontrado en i2c! ({len(resultados_i2c)} opciones)")
                for r_i2c in resultados_i2c:
                    nombre_i2c = r_i2c['producto'].upper()
                    
                    # REGLA JOA: Marco solo permitido si es Service Pack / Original
                    if "MARCO" in nombre_i2c:
                        if "SERVICE PACK" not in nombre_i2c and "ORIGINAL" not in nombre_i2c:
                            continue
                        
                    repuestos_filtrados.append({
                        'nombre_consolidado': f"[CALIDAD: {r_i2c['producto'].replace('Pantalla ', '')}] {r_i2c['producto']} {modelo_limpio}",
                        'precio': r_i2c['precio_costo']
                    })
        
        # ---------------------------------------------------------
        # PROCESAMIENTO FINAL, FILTRADO Y ORDEN
        # ---------------------------------------------------------
        if not repuestos_filtrados:
            return """ATENCIÓN: Búsqueda completada. 0 resultados en la base de datos y proveedores externos.
            INSTRUCCIÓN IA: Dile al cliente que lamentablemente no nos figura stock de ese repuesto en este momento, pero que le pasas la consulta a los chicos del taller para ver si se puede conseguir a pedido. 
            OBLIGATORIO: Agrega al final de tu respuesta la etiqueta secreta: [ASISTENCIA_HUMANA]"""
            
        # NUEVO SISTEMA DE PRIORIDADES DE JOA
        def calcular_prioridad(nombre):
            n = nombre.upper()
            if "OLED" in n: return 1.0
            elif "SUNLONG" in n or "JK" in n or "CROWN" in n or "MS" in n: return 2.0
            elif "ORIG" in n or "ORI" in n or "SERVICE PACK" in n: return 3.0
            elif "INCELL" in n: return 4.0
            return 5.0
        
        repuestos_ordenados = sorted(repuestos_filtrados, key=lambda x: calcular_prioridad(x['nombre_consolidado']))
        
        mejores_opciones = repuestos_ordenados[:2]
        
        opciones_texto = ""
        for i, r in enumerate(mejores_opciones): 
            lista, efectivo, tarjeta, cuota = aplicar_calculadora(r['precio'])
            
            # 🚨 NUEVA REGLA DE JOA: LÍMITE DE $300.000 🚨
            if efectivo >= 300000 or lista >= 300000:
                return """ATENCIÓN: El repuesto es de ALTA GAMA y supera el límite de $300.000. 
                INSTRUCCIÓN IA: TIENES PROHIBIDO DAR EL PRECIO. Dile ágilmente al cliente: 'Che, te cuento que ese repuesto es de alta gama. Le paso el caso a los chicos del taller para que lo revisen bien y te armen una cotización a medida.'
                OBLIGATORIO: Agrega al final de tu respuesta la etiqueta secreta: [ASISTENCIA_HUMANA]"""

            opciones_texto += f"Opción {i+1}: {r['nombre_consolidado']} -> EFVO: ${efectivo} | LISTA: ${lista} | TARJETA: ${tarjeta} (3 de ${cuota})\n"
        
        instruccion_final = """INSTRUCCIÓN IA: Aplica tu ESTRATEGIA DE VENTA DE PANTALLAS. 
        Ofrece SIEMPRE SOLO LA OPCIÓN 1 por defecto usando el formato de UNA SOLA OPCIÓN de tus reglas. No menciones marcas raras. 
        Si la opción 2 es Original/Service Pack, guárdatela bajo la manga."""

        return f"ATENCIÓN: Encontré stock. Estos son los datos de sistema (NO SE LOS LEAS ASÍ AL CLIENTE):\n{opciones_texto}\n{instruccion_final}"
            
    except Exception as e:
        import traceback
        print(f"🚨 [ERROR]:\n{traceback.format_exc()}")
        return "Error técnico al calcular repuesto." 