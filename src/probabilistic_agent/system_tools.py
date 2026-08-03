import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool
import requests as req
import json

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
    
    if "pantalla" in tipo_rep or "modulo" in tipo_rep or "display" in tipo_rep:
        sinonimos_busqueda = ["modulo", "pantalla", "display"]
    elif "pin" in tipo_rep or "carga" in tipo_rep or "conector" in tipo_rep:
        sinonimos_busqueda = ["pin", "conector", "placa", "flex de carga"]
    elif "bateria" in tipo_rep or "pila" in tipo_rep:
        sinonimos_busqueda = ["bateria", "bat"]
    elif "tapa" in tipo_rep or "trasera" in tipo_rep:
        sinonimos_busqueda = ["tapa", "vidrio trasero"]

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
        
        for proveedor in PRIORIDAD_PROVEEDORES:
            respuesta = supabase.table("productos").select("*").eq("client_id", proveedor).or_(filtro_or).execute()
            resultados = respuesta.data
            
            if not resultados: continue 
                
            repuestos_filtrados = []
            for rep in resultados:
                nombre_bd = str(rep.get('nombre_consolidado', '')).upper()
                texto_bd_lower = nombre_bd.lower().replace('ó', 'o').replace('á', 'a').replace('í', 'i')
                
                # Chequeamos si alguno de los sinónimos (ej: "conector") está en el nombre
                coincide_tipo = any(sin in texto_bd_lower for sin in sinonimos_busqueda)
                
                if coincide_tipo:
                    # Aplicamos validación láser de modelo 
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
                    
            if not repuestos_filtrados: continue
                
            if len(repuestos_filtrados) == 1:
                repuesto = repuestos_filtrados[0]
                lista, efectivo, tarjeta, cuota = aplicar_calculadora(repuesto['precio'])
                return f"""ÉXITO. Encontré el repuesto: {repuesto['nombre_consolidado']}.
                PRECIOS FINALES:
                - Efectivo: ${efectivo}
                - Transferencia (Lista): ${lista}
                - Tarjeta: ${tarjeta} (3 cuotas de ${cuota})
                INSTRUCCIÓN IA: Es un repuesto simple. Usa el formato de UNA SOLA OPCIÓN. PROHIBIDO mencionar calidad, premium, original o alternativas. Solo pasa los números."""
            
            else:
                def calcular_prioridad(nombre):
                    n = nombre.upper()
                    base = 6.0 
                    if "OLED" in n: base = 1.0
                    elif "ORIG" in n or "ORI" in n: base = 2.0
                    elif "SUNLONG" in n or "JK" in n: base = 3.0
                    elif "MARCO" in n or "C/MARCO" in n: base = 4.0
                    elif "INCELL" in n: base = 5.0
                    modificador = -0.1 if "SOFT" in n else (0.1 if "HARD" in n else 0.0)
                    return base + modificador
                
                repuestos_ordenados = sorted(repuestos_filtrados, key=lambda x: calcular_prioridad(x['nombre_consolidado']))
                
                # 🧠 LÓGICA INTELIGENTE: 2 opciones para pantallas, 1 sola para el resto
                es_pantalla = any(s in sinonimos_busqueda for s in ["modulo", "pantalla", "display"])
                cantidad_opciones = 2 if es_pantalla else 1
                
                mejores_opciones = repuestos_ordenados[:cantidad_opciones]
                
                opciones_texto = ""
                for r in mejores_opciones: 
                    lista, efectivo, tarjeta, cuota = aplicar_calculadora(r['precio'])
                    opciones_texto += f"- {r['nombre_consolidado']} -> EFVO: ${efectivo} | LISTA: ${lista} | TARJETA: ${tarjeta} (3 de ${cuota})\n"
                
                # 👇 EL CANDADO DE CALIDADES
                if es_pantalla:
                    instruccion_final = "INSTRUCCIÓN IA: Es un módulo/pantalla. Usa el formato de DOS OPCIONES y aplica tus reglas de traducción de calidades (Premium, Alternativa)."
                else:
                    instruccion_final = "INSTRUCCIÓN IA: Es un repuesto simple (pin, batería, tapa). Usa el formato de UNA SOLA OPCIÓN. Tienes ESTRICTAMENTE PROHIBIDO mencionar palabras como 'calidad', 'premium', 'original' o 'alternativa'. Solo pasa el precio directo."

                return f"ATENCIÓN: Encontré opciones. Te paso las {len(mejores_opciones)} MEJORES:\n{opciones_texto}\n{instruccion_final}"
                
        # 👇 4. RED DE SEGURIDAD (SIN STOCK) - Fuera del bucle for
        return """ATENCIÓN: Búsqueda completada. 0 resultados en la base de datos.
        INSTRUCCIÓN IA: Dile al cliente que lamentablemente no nos figura stock de ese repuesto en este momento, pero que le pasas la consulta a los chicos del taller para ver si se puede conseguir a pedido. 
        OBLIGATORIO: Agrega al final de tu respuesta la etiqueta secreta: [ASISTENCIA_HUMANA]"""
        
    except Exception as e:
        import traceback
        print(f"🚨 [ERROR]:\n{traceback.format_exc()}")
        return "Error técnico al calcular repuesto."