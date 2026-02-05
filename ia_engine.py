import streamlit as st
from google import genai
from google.oauth2 import service_account
from PIL import Image
import io
import config_prompt

def conectar_vertex(creds_dict):
    """Establece la conexión usando el nuevo SDK de GenAI."""
    raw_key = str(creds_dict.get("private_key", ""))
    clean_key = raw_key.strip().strip('"').strip("'").replace("\\n", "\n")
    creds_dict["private_key"] = clean_key
    google_creds = service_account.Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Usamos el cliente genai que tú ya conoces
    return genai.Client(vertexai=True, project=creds_dict.get("project_id"), 
                        location="us-central1", credentials=google_creds)

def buscar_mercado_capa1(client, marca, modelo, anio):
    """CAPA 1: Búsqueda de mercado con Google Search y 2.5 Pro."""
    prompt = config_prompt.prompt_capa_1_buscador(marca, modelo, anio)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt],
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0.35,
                "max_output_tokens": 4096
            }
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 1: {str(e)}"

def analizar_peritaje_capa3(client, marca, modelo, precio_base, observaciones, ubicacion, lista_fotos):
    """CAPA 3: Peritaje visual con optimización de fotos."""
    fotos_ia = []
    for foto in lista_fotos:
        img = Image.open(foto).convert("RGB")
        img.thumbnail((800, 800)) 
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75) 
        buf.seek(0)
        fotos_ia.append(Image.open(buf))

    prompt = config_prompt.prompt_capa_3_perito(marca, modelo, precio_base, observaciones, ubicacion)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt] + fotos_ia,
            config={
                "temperature": 0.35,
                "max_output_tokens": 4096
            }
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 3: {str(e)}"
