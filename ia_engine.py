import streamlit as st
from google import genai
from google.oauth2 import service_account
from PIL import Image
import io
import config_prompt

def conectar_vertex(creds_dict):
    """Establece la conexión segura con Vertex AI usando Service Account."""
    raw_key = str(creds_dict.get("private_key", ""))
    clean_key = raw_key.strip().strip('"').strip("'").replace("\\n", "\n")
    creds_dict["private_key"] = clean_key
    google_creds = service_account.Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return genai.Client(vertexai=True, project=creds_dict.get("project_id"), 
                        location="us-central1", credentials=google_creds)

def buscar_mercado_capa1(client, marca, modelo, anio):
    [cite_start]"""Ejecuta la Capa 1: Búsqueda de anuncios reales con Google Search[cite: 7]."""
    prompt = config_prompt.prompt_capa_1_buscador(marca, modelo, anio)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-pro-exp-02-05", # O tu versión preferida
            contents=[prompt],
            config={"tools": [{"google_search": {}}]}
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 1: {str(e)}"

def analizar_peritaje_capa3(client, marca, modelo, precio_base, observaciones, ubicacion, lista_fotos):
    """Ejecuta la Capa 3: Análisis visual y ajuste final de precio."""
    
    # Optimización de fotos para Cloud Run (Evita reinicios por RAM)
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
            model="gemini-2.0-flash", # Flash es ideal para visión rápida
            contents=[prompt] + fotos_ia,
            config={"temperature": 0.2}
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 3: {str(e)}"
