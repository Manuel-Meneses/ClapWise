import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

CONFIGURACION_PROVEEDORES = [
    {
        "id_base_datos": "proveedor_mundo_parts", 
        "url": "https://docs.google.com/spreadsheets/d/1c39kYssBH8TWE4JPZ8c4xy9OJ4RnsCme/export?format=xlsx",
        "pestanas": ["Modulos", "Baterias", "Camaras", "Tapas / Marcos", "Porta Sim / FPC", "Placa de carga", "Home / Huella", "Lente de Camara"]
    },
    {
        "id_base_datos": "proveedor_syphon", 
        "url": "https://docs.google.com/spreadsheets/d/1ewZCtjpTRNzsOLQXArrzc8ayMGms5m9F/export?format=xlsx",
        "pestanas": ["modulos", "tapas", "baterias"]
    },
    {
        "id_base_datos": "proveedor_sintren", 
        "url": "https://docs.google.com/spreadsheets/d/19zx6Q0IhpMOgnYi9Bo0WBJIG4up6Pi8M2e9UcfR7hdI/export?format=xlsx",
        "pestanas": ["modulos", "baterias"]
    }
]

def sincronizar_proveedores_adicionales():
    print("📥 Iniciando extracción automatizada de proveedores...\n")
    
    for config in CONFIGURACION_PROVEEDORES:
        prov_id = config["id_base_datos"]
        url_sheet = config["url"]
        
        print(f"============================================")
        print(f"🚀 Conectando con {prov_id}...")
        
        try:
            archivo_excel = pd.ExcelFile(url_sheet)
            pestanas_reales = {str(nombre).strip().lower(): nombre for nombre in archivo_excel.sheet_names}
            lote_total_proveedor = []
            
            for nombre_buscado in config["pestanas"]:
                print(f"  🔍 Analizando pestaña: '{nombre_buscado}'...")
                
                if nombre_buscado.lower() not in pestanas_reales:
                    print(f"    ⚠️ Pestaña no encontrada. Saltando.")
                    continue
                    
                nombre_real = pestanas_reales[nombre_buscado.lower()]
                df = pd.read_excel(archivo_excel, sheet_name=nombre_real, header=None)
                
                # ========================================================
                # LA MAGIA ANTI-PÉRDIDA: Rellenamos las celdas combinadas 
                # hacia abajo (Forward Fill) en todo el DataFrame
                # ========================================================
                df = df.ffill(axis=0)
                
                idx_cabecera = -1
                pares_columnas = [] 
                
                for idx, row in df.head(20).iterrows():
                    row_str = [str(val).lower().strip() for val in row.values]
                    indices_precio = [i for i, val in enumerate(row_str) if "precio" in val or "costo" in val]
                    
                    if indices_precio:
                        idx_cabecera = idx
                        for col_precio in indices_precio:
                            if col_precio > 0:
                                pares_columnas.append((col_precio - 1, col_precio))
                        break 
                
                if not pares_columnas:
                    print(f"    ⚠️ No se detectó ninguna columna de 'Precio' o 'Costo'. Saltando.")
                    continue
                
                df_datos = df.iloc[idx_cabecera + 1:]
                
                for col_mod, col_prec in pares_columnas:
                    marca_actual = ""
                    
                    for index, row in df_datos.iterrows():
                        repuesto_raw = str(row[col_mod]).strip()
                        precio_raw = row[col_prec]
                        
                        # 1. Lógica para detectar títulos de categoría (Ej: "SAMSUNG" sin precio al lado)
                        if repuesto_raw and repuesto_raw.lower() not in ['nan', 'none'] and pd.isna(precio_raw):
                            if "sin stock" not in repuesto_raw.lower():
                                marca_actual = repuesto_raw
                            continue
                            
                        # 2. Saltamos celdas basura o vacías
                        if repuesto_raw.lower() in ['nan', 'none', ''] or "sin stock" in repuesto_raw.lower():
                            continue
                            
                        # 3. Saltamos repuestos que no tienen precio cargado
                        if pd.isna(precio_raw):
                            continue

                        # 4. LIMPIEZA INTELIGENTE DE PRECIOS
                        try:
                            if "sin stock" in str(precio_raw).lower():
                                continue
                                
                            if isinstance(precio_raw, (int, float)):
                                precio_limpio = float(precio_raw)
                                # Corrección de decimales de Excel
                                if 0 < precio_limpio < 1000:
                                    precio_limpio = precio_limpio * 1000
                            else:
                                precio_str = str(precio_raw).strip().replace('$', '').replace(' ', '')
                                if precio_str.endswith(',00') or precio_str.endswith('.00'):
                                    precio_str = precio_str[:-3]
                                precio_str = precio_str.replace('.', '').replace(',', '')
                                precio_limpio = float(precio_str)
                                
                            if precio_limpio <= 0:
                                continue
                        except ValueError:
                            continue 
                            
                        nombre_final = f"{marca_actual} {repuesto_raw}" if marca_actual else repuesto_raw
                        
                        producto_db = {
                            "client_id": prov_id, 
                            "nombre_consolidado": f"[{nombre_real.upper()}] {nombre_final}",
                            "precio": precio_limpio,
                            "stock": 99 
                        }
                        lote_total_proveedor.append(producto_db)
            
            if lote_total_proveedor:
                print(f"\n  📦 {prov_id}: Extracción completa. {len(lote_total_proveedor)} productos listos.")
                # Borramos todo el catálogo viejo y metemos el nuevo (Evita repuestos fantasma)
                supabase.table("productos").delete().eq("client_id", prov_id).execute()
                supabase.table("productos").insert(lote_total_proveedor).execute()
                print(f"  ✅ Catálogo inyectado en Supabase.\n")
            else:
                print(f"  ⚠️ No se extrajeron datos para {prov_id}.\n")
                
        except Exception as e:
            import traceback
            print(f"  🚨 Error crítico con {prov_id}:\n{traceback.format_exc()}\n")
            
    print("🎉 ¡SISTEMA DE PROVEEDORES SINCRONIZADO AL 100%!")

if __name__ == "__main__":
    sincronizar_proveedores_adicionales()