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
    
    filtro_adicional = "módulo" if "pantalla" in tipo_repuesto.lower() else tipo_repuesto.lower()
    PRIORIDAD_PROVEEDORES = ["proveedor_one_services"]

    try:
        # 1. Descargar la matriz de cálculo
        respuesta_matriz = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", "matriz_calculo_interna").execute()
        matriz_raw = respuesta_matriz.data[0]["reglas_calculadora"] if respuesta_matriz.data else "[]"
        matriz = json.loads(matriz_raw)
        
        # Ordenamos de mayor a menor para que la lógica de rangos funcione perfecto
        matriz = sorted(matriz, key=lambda x: x['min'], reverse=True)

        # Función interna para calcular los precios al vuelo
        def aplicar_calculadora(costo_base):
            mo, dto, rec = 35000, 0.16, 0.25 # Valores por defecto de emergencia
            for rango in matriz:
                if costo_base >= rango['min']:
                    mo = rango['mo']
                    dto = rango['dto']
                    rec = rango['rec']
                    break
            
            lista = costo_base + mo
            efectivo = lista * (1 - dto)
            tarjeta = lista * (1 + rec)
            cuota = tarjeta / 3
            return int(lista), int(efectivo), int(tarjeta), int(cuota)

        # 2. Búsqueda de repuestos
        modelo_limpio = modelo.replace("Samsung", "").replace("samsung", "").strip()
        if not modelo_limpio: modelo_limpio = modelo 
        
        for proveedor in PRIORIDAD_PROVEEDORES:
            respuesta = supabase.table("productos").select("*").eq("client_id", proveedor).ilike("nombre_consolidado", f"%{modelo_limpio}%").execute()
            resultados = respuesta.data
            
            if not resultados: continue 
                
            repuestos_filtrados = []
            for rep in resultados:
                texto_bd = str(rep.get('nombre_consolidado', '')).lower().replace('ó', 'o')
                if filtro_adicional.replace('ó', 'o') in texto_bd:
                    repuestos_filtrados.append(rep)
                    
            if not repuestos_filtrados: continue
                
            # ¡BINGO! UN SOLO REPUESTO
            if len(repuestos_filtrados) == 1:
                repuesto = repuestos_filtrados[0]
                lista, efectivo, tarjeta, cuota = aplicar_calculadora(repuesto['precio'])
                
                return f"""ÉXITO. Encontré el repuesto: {repuesto['nombre_consolidado']}.
                PRECIOS FINALES YA CALCULADOS PARA EL CLIENTE:
                - Efectivo: ${efectivo}
                - Transferencia (Lista): ${lista}
                - Tarjeta: ${tarjeta} (3 cuotas de ${cuota})
                INSTRUCCIÓN IA: Arma tu respuesta final usando ESTOS NÚMEROS EXACTOS. No apliques ninguna suma o descuento adicional."""
            
            else:
                # 🧠 LÓGICA DE PRIORIDADES DE ONE SERVICES CORREGIDA
                def calcular_prioridad(nombre):
                    n = nombre.upper()
                    
                    # 1. Definimos el peso de la CALIDAD PRINCIPAL (más bajo es mejor)
                    base = 6.0 # Por defecto, si no conocemos la marca, va al final
                    
                    if "OLED" in n:
                        base = 1.0
                    elif "ORIG" in n or "ORI" in n:
                        base = 2.0
                    elif "SUNLONG" in n or "JK" in n:
                        base = 3.0
                    elif "MARCO" in n or "C/MARCO" in n:
                        base = 4.0
                    elif "INCELL" in n:
                        base = 5.0
                        
                    # 2. Definimos el modificador de CARACTERÍSTICA (Desempate)
                    # Si la base es igual (ej: dos OLED), Soft resta puntos (lo hace mejor) y Hard suma (lo hace peor)
                    modificador = 0.0
                    if "SOFT" in n:
                        modificador = -0.1
                    elif "HARD" in n:
                        modificador = 0.1
                        
                    # El resultado final es la mezcla perfecta sin que se pisen
                    return base + modificador
                
                # Ordenamos la lista de repuestos usando tu regla de prioridades
                repuestos_ordenados = sorted(repuestos_filtrados, key=lambda x: calcular_prioridad(x['nombre_consolidado']))
                
                # CORTAMOS LA LISTA: Solo le pasamos a Gemini las 2 mejores opciones
                mejores_opciones = repuestos_ordenados[:2]
                
                opciones_texto = ""
                for r in mejores_opciones: 
                    lista, efectivo, tarjeta, cuota = aplicar_calculadora(r['precio'])
                    opciones_texto += f"- {r['nombre_consolidado']} -> EFVO: ${efectivo} | LISTA: ${lista} | TARJETA: ${tarjeta} (3 de ${cuota})\n"
                
                return f"""ATENCIÓN: Encontré varias calidades, pero ya seleccioné las {len(mejores_opciones)} MEJORES para ofrecerle al cliente.
                Acá tenés los precios FINALES para cada versión:
                {opciones_texto}
                INSTRUCCIÓN IA: Ofrece ESTAS opciones al cliente aplicando tus reglas comerciales de calidades."""
    except Exception as e:
        import traceback
        print(f"🚨 [ERROR]:\n{traceback.format_exc()}")
        return "Error técnico al calcular repuesto. Pídele al cliente que espere un momento."