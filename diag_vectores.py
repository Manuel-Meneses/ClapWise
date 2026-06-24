import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No se encontró la GOOGLE_API_KEY.")
    exit()

print("Buscando motores de vectorización en Google...\n")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("✅ Modelos de VECTORES disponibles:")
    for model in data.get('models', []):
        if 'embedContent' in model.get('supportedGenerationMethods', []):
            print(f"- {model['name']}")
else:
    print(f"❌ Error de conexión: {response.status_code}")