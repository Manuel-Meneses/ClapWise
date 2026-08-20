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
def buscar_costo_repuesto_real(modelo: str, tipo_repuesto: str) -> str:
    """Busca repuestos en la base unificada de Joa, aplica la calculadora y devuelve los precios finales al cliente."""
    print(f"\n🔍 [SISTEMA] Buscando: '{modelo}' | Repuesto: '{tipo_repuesto}'")
    
    # 1. ESTANDARIZAR LA BÚSQUEDA (Debe coincidir con las etiquetas del Excel)
    tipo_rep = tipo_repuesto.lower()
    if "pantalla" in tipo_rep or "modulo" in tipo_rep or "display" in tipo_rep:
        tag_repuesto = "[PANTALLA]"
    elif "bateria" in tipo_rep or "pila" in tipo_rep:
        tag_repuesto = "[BATERIA]"
    elif "pin" in tipo_rep or "carga" in tipo_rep or "conector" in tipo_rep:
        tag_repuesto = "[PIN CARGA]"
    else:
        tag_repuesto = "[PANTALLA]" # Por defecto

    try:
        # 2. TRAER LA CALCULADORA FINANCIERA (Leemos los porcentajes del Excel)
        respuesta_matriz = supabase.table("configuracion_clientes").select("reglas_calculadora").eq("client_id", "matriz_calculo_interna").execute()
        
        # Valores por defecto por si falla algo
        dto_efectivo = 0.10
        rec_3_cuotas = 0.18
        rec_6_cuotas = 0.25 # (Opcional, si usa 6 cuotas)
        
        if respuesta_matriz.data:
            matriz_data = json.loads(respuesta_matriz.data[0]["reglas_calculadora"])
            dto_efectivo = float(matriz_data.get("descuento_efectivo", 0.10))
            rec_3_cuotas = float(matriz_data.get("recargo_3_cuotas", 0.18))

        # 3. BÚSQUEDA INTELIGENTE PERO SIMPLE
        modelo_limpio = modelo.upper().replace("SAMSUNG", "").replace("MOTOROLA", "").strip()
        
        # Traemos de Supabase SOLO los repuestos de Joa y de ese tipo (Ej: todas las "[PANTALLA]")
        respuesta_productos = supabase.table("productos").select("*").eq("client_id", "proveedor_joaquin").ilike("nombre_consolidado", f"{tag_repuesto}%").execute()
        resultados = respuesta_productos.data
        
        if not resultados:
            return """🛑 ALERTA DE SISTEMA: 0 RESULTADOS. No hay stock de este repuesto.
            TU ÚNICA RESPUESTA PERMITIDA ES: "No me figura stock de ese repuesto en el sistema ahora mismo. De todas formas, ahí le aviso a los chicos del taller para que revisen si lo podemos conseguir."
            OBLIGATORIO: Agrega al final la etiqueta secreta: [ASISTENCIA_HUMANA]"""
            
        # Filtramos por modelo exacto (Busca que todas las palabras pedidas estén en el nombre del Excel)
        repuestos_filtrados = []
        tokens = modelo_limpio.split()
        for rep in resultados:
            nombre_bd = rep["nombre_consolidado"].upper()
            coincide_todo = True
            for t in tokens:
                if str(t).strip() not in nombre_bd:
                    coincide_todo = False
                    break
            if coincide_todo:
                repuestos_filtrados.append(rep)
                
        if not repuestos_filtrados:
            return """🛑 ALERTA DE SISTEMA: 0 RESULTADOS. No hay stock de este repuesto.
            TU ÚNICA RESPUESTA PERMITIDA ES: "No me figura stock de ese repuesto en el sistema ahora mismo. De todas formas, ahí le aviso a los chicos del taller para que revisen si lo podemos conseguir."
            OBLIGATORIO: Agrega al final la etiqueta secreta: [ASISTENCIA_HUMANA]"""
             
        # Como es el Excel de Joa, no hay duplicados de calidades. Tomamos el primer resultado que coincide.
        repuesto_elegido = repuestos_filtrados[0]
        
        # 4. LA MATEMÁTICA PURA (Calculamos el abanico de precios)
        precio_lista = float(repuesto_elegido["precio"])
        efectivo = int(precio_lista * (1 - dto_efectivo))
        tarjeta_3 = int(precio_lista * (1 + rec_3_cuotas))
        cuota_3 = int(tarjeta_3 / 3)
        tarjeta_6 = int(precio_lista * (1 + rec_6_cuotas))
        cuota_6 = int(tarjeta_6 / 6)
        
        # 5. EMPAQUETADO PARA GASPAR
        opciones_texto = f"Opción 1: {repuesto_elegido['nombre_consolidado']} -> EFVO: ${efectivo} | LISTA: ${int(precio_lista)} | TARJETA: ${tarjeta_3} (3 de ${cuota_3}) | TARJETA 6: ${tarjeta_6} (6 de ${cuota_6})\n"

        instruccion_final = "INSTRUCCIÓN IA: Ofrece este precio al cliente usando OBLIGATORIAMENTE tu formato de cotización esperado. No hables de calidades, el precio ya es final."

        return f"ATENCIÓN: Encontré stock. Estos son los datos de sistema:\n{opciones_texto}\n{instruccion_final}" 

    except Exception as e:
        print(f"🚨 [ERROR]: {e}")
        return "Error técnico al calcular repuesto."