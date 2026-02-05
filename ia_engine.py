import streamlit as st
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, GoogleSearchRetrieval
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
    
    vertexai.init(
        project=creds_dict.get("project_id"), 
        location="us-central1", 
        credentials=google_creds
    )
    return True

def buscar_mercado_capa1(marca, modelo, anio):
    """CAPA 1: Búsqueda con motor Gemini 2.5 Pro y Google Search."""
    herramienta_busqueda = Tool.from_google_search_retrieval(
        google_search_retrieval=GoogleSearchRetrieval()
    )
    
    # Usamos el modelo 2.5 Pro como me has pedido
    model = GenerativeModel("gemini-2.5-pro") 
    
    prompt = config_prompt.prompt_capa_1_buscador(marca, modelo, anio)
    
    try:
        response = model.generate_content(
            prompt,
            tools=[herramienta_busqueda],
            generation_config={
                "temperature": 0.35,
                "max_output_tokens": 4096,
            }
        )
        return response.text
    except Exception as e:
        # Si el modelo 2.5 no está disponible en tu región, te avisará aquí
        return f"Error en Capa 1 (Modelo 2.5 Pro): {str(e)}"

def analizar_peritaje_capa3(marca, modelo, precio_base, observaciones, ubicacion, lista_fotos):
    """CAPA 3: Peritaje visual con el mismo motor 2.5 Pro."""
    from vertexai.generative_models import Part
    
    fotos_ia = []
    for foto in lista_fotos:
        img = Image.open(foto).convert("RGB")
        img.thumbnail((800, 800)) 
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75) 
        buf.seek(0)
        fotos_ia.append(Part.from_data(data=buf.getvalue(), mime_type="image/jpeg"))

    model = GenerativeModel("gemini-2.5-pro") 
    prompt = config_prompt.prompt_capa_3_perito(marca, modelo, precio_base, observaciones, ubicacion)

    try:
        response = model.generate_content(
            [prompt] + fotos_ia,
            generation_config={
                "temperature": 0.35,
                "max_output_tokens": 4096,
            }
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 3: {str(e)}"
