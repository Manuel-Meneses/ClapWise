import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool

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
    """Alerta a humano."""
    return "Notificación enviada a un asesor."


@tool
def buscar_costo_repuesto_real(modelo: str, tipo_repuesto: str) -> str:
    """Busca el costo base iterando por los proveedores en orden de prioridad."""
    print(f"\n🔍 [IA BUSCANDO] Modelo: '{modelo}' | Repuesto: '{tipo_repuesto}'")
    
    filtro_adicional = "módulo" if "pantalla" in tipo_repuesto.lower() else tipo_repuesto.lower()
    
    # 🧠 ORDEN DE PRIORIDAD: El bot va a buscar en este orden exacto.
    # Podés cambiar el orden moviendo los nombres de lugar.
    PRIORIDAD_PROVEEDORES = [
        "proveedor_i2c", 
        "proveedor_syphon", 
        "proveedor_sintren"
    ]

    try:
        modelo_limpio = modelo.replace("Samsung", "").replace("samsung", "").strip()
        if not modelo_limpio: modelo_limpio = modelo 
        
        # El bot recorre la lista uno por uno
        for proveedor in PRIORIDAD_PROVEEDORES:
            print(f"Buscando en {proveedor}...")
            
            respuesta = supabase.table("productos") \
                .select("*") \
                .eq("client_id", proveedor) \
                .ilike("nombre_consolidado", f"%{modelo_limpio}%") \
                .execute()
            
            resultados = respuesta.data
            
            # Si este proveedor no lo tiene, saltamos al siguiente proveedor con 'continue'
            if not resultados:
                continue 
                
            # Si lo tiene, filtramos que sea el repuesto correcto (ej: módulo)
            repuestos_filtrados = []
            for rep in resultados:
                texto_bd = str(rep.get('nombre_consolidado', '')).lower().replace('ó', 'o')
                if filtro_adicional.replace('ó', 'o') in texto_bd:
                    repuestos_filtrados.append(rep)
                    
            # Si después de filtrar no quedó nada, pasamos al siguiente proveedor
            if not repuestos_filtrados:
                continue
                
            # ¡BINGO! Lo encontramos. Frenamos la búsqueda y aplicamos la lógica.
            if len(repuestos_filtrados) == 1:
                repuesto_elegido = repuestos_filtrados[0]
                nombre_repuesto = repuesto_elegido['nombre_consolidado']
                costo_proveedor = repuesto_elegido['precio'] 
                
                print(f"✅ [ÉXITO] Lo tenía el proveedor: {proveedor} | Costo: ${costo_proveedor}")
                
                return f"ÉXITO. Encontré el repuesto: {nombre_repuesto}. El COSTO BASE es de ${costo_proveedor}. Aplica la calculadora interna de la tienda a este costo para dar los precios finales al cliente."
            
            else:
                print(f"⚠️ [AMBIGÜEDAD] Encontrado en {proveedor} pero hay {len(repuestos_filtrados)} variantes.")
                
                opciones = ""
                for r in repuestos_filtrados[:6]: 
                    opciones += f"- {r['nombre_consolidado']} (Costo base: ${r['precio']})\n"
                
                return f"""ATENCIÓN: Encontré VARIAS versiones distintas para el modelo '{modelo}'. NO apliques la calculadora todavía. 
                Respóndele al cliente que existen diferentes variantes y pregúntale cuál de estas es la suya:
                {opciones}
                
                INSTRUCCIÓN EXTRA: Si el cliente te responde que NO SABE o no está seguro de cuál es su modelo, NO te trabes. 
                Ofrécele un rango de precios aproximado (desde el más barato al más caro de la lista), dile que puede buscar 
                el modelo exacto en 'Ajustes > Acerca del teléfono', o invítalo a que se acerque al local para que lo revisemos sin cargo."""

        # Si el bot pasó por toda la lista (terminó el 'for') y ninguno lo tenía:
        print("❌ [AGOTADO] Ningún proveedor tiene este repuesto.")
        return f"Revisé los catálogos de todos nuestros proveedores y ninguno tiene stock del repuesto '{tipo_repuesto}' para el modelo '{modelo}' en este momento. Informale esto al cliente."

    except Exception as e:
        import traceback
        print(f"🚨 [ERROR]:\n{traceback.format_exc()}")
        return f"Error técnico al buscar repuesto: {str(e)}"