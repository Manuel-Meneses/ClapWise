import os
import requests
from dotenv import load_dotenv

# Cargar tu GOOGLE_API_KEY desde el archivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No se encontró la GOOGLE_API_KEY. Revisa tu archivo .env")
    exit()

print("Conectando a los servidores de Google...\n")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("✅ Modelos disponibles para tu API Key:")
    for model in data.get('models', []):
        # Filtramos solo los que sirven para generar texto/chat
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            nombre_limpio = model['name'].replace('models/', '')
            print(f"- {nombre_limpio}")
else:
    print(f"❌ Error de conexión: {response.status_code}")
    print(response.text)