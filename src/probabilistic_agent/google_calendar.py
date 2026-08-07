import os
import json # Agregamos esto
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ==========================================
# CONFIGURACIÓN DE TU CALENDARIO
# ==========================================
CALENDAR_ID = "33c7681e8cb2aaf44b7ec4d1eb639dd52859f54fbd65d0a2408178a9930649e3@group.calendar.google.com" 
# ==========================================

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def obtener_servicio_calendar():
    """Autentica con Google usando la variable de entorno."""
    try:
        # 1. Buscamos el texto del JSON en el entorno del servidor
        credenciales_json_string = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        
        if not credenciales_json_string:
            print("❌ Error: No se encontró la variable GOOGLE_CREDENTIALS_JSON")
            return None

        # 2. Convertimos ese texto nuevamente a un formato que Google entienda (un diccionario)
        info_credenciales = json.loads(credenciales_json_string)

        # 3. Nos autenticamos pasándole la información directamente de la memoria, sin tocar archivos
        creds = service_account.Credentials.from_service_account_info(
            info_credenciales, scopes=SCOPES)
            
        service = build('calendar', 'v3', credentials=creds)
        return service
        
    except Exception as e:
        print(f"❌ Error al conectar con Google Calendar: {e}")
        return None

def insertar_evento_turno(nombre_cliente: str, equipo_y_falla: str, fecha_hora_iso: str) -> str:
    """
    Se conecta a Google Calendar y crea el evento del turno.
    Devuelve un mensaje de éxito o de error.
    """
    service = obtener_servicio_calendar()
    if not service:
        return "Error interno: No se pudo conectar al calendario."

    # Google Calendar necesita saber cuándo TERMINA el turno. 
    # Para celulares, asumimos que un turno dura 1 hora por defecto (como dice tu regla).
    # Como la IA nos manda ISO 8601 (ej: 2026-08-10T10:00:00-03:00), 
    # lo más fácil para no complicarnos con Python es decirle a Google Calendar
    # que empiece en ese horario y lo marque, nosotros no nos preocupamos por la matemática del final
    # si usamos el formato datetime directo. Pero por prolijidad, vamos a procesarlo.

    from datetime import datetime, timedelta
    
    try:
        # Convertimos el string que manda Gemini (ej: 2026-08-10T10:00:00-03:00) a un objeto fecha de Python
        fecha_inicio = datetime.fromisoformat(fecha_hora_iso)
        # Le sumamos 1 hora para el fin del turno
        fecha_fin = fecha_inicio + timedelta(hours=1)
        
        # Volvemos a convertir a texto ISO para dárselo a Google
        inicio_str = fecha_inicio.isoformat()
        fin_str = fecha_fin.isoformat()
    except Exception as e:
        print(f"Error parseando fecha: {e}. Se usará la original.")
        # Fallback de emergencia si Gemini manda la fecha medio rara
        inicio_str = fecha_hora_iso
        fin_str = fecha_hora_iso # Evento de 0 minutos, pero al menos aparece

    # Armamos la "caja" del evento que le vamos a mandar a Google
    evento = {
      'summary': f'📱 TURNO: {nombre_cliente}',
      'description': f'Equipo y falla a reparar:\n{equipo_y_falla}\n\nAgendado por: Gaspar (Bot)',
      'start': {
        'dateTime': inicio_str,
        'timeZone': 'America/Argentina/Cordoba', # O 'America/Buenos_Aires'
      },
      'end': {
        'dateTime': fin_str,
        'timeZone': 'America/Argentina/Cordoba',
      },
      'colorId': '11', # 11 es color Rojo en Google Calendar (para que llame la atención)
    }

    try:
        # ¡Apretamos el gatillo! Mandamos el evento a Google
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
        url_evento = event_result.get('htmlLink')
        print(f"✅ ¡Turno creado en Calendar! URL: {url_evento}")
        return "Turno agendado exitosamente en el calendario."
    except Exception as e:
        error_msg = f"❌ Error al crear el evento en Calendar: {e}"
        print(error_msg)
        return "Error al intentar guardar el turno en el calendario."