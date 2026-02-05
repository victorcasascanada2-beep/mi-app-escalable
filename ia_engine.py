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
    # Limpieza de la clave privada
    raw_key = str(creds_dict.get("private_key", ""))
    clean_key = raw_key.strip().strip('"').strip("'").replace("\\n", "\n")
    creds_dict["private_key"] = clean_key
    
    google_creds = service_account.Credentials.from_service_account_info(creds_dict)
    
    # Inicialización oficial de Vertex
    vertexai.init(
        project=creds_dict.get("project_id"), 
        location="us-central1", 
        credentials=google_creds
    )
    return True # Solo confirmamos la conexión

def buscar_mercado_capa1(marca, modelo, anio):
    """Ejecuta la Capa 1 usando Google Search en Vertex AI."""
    # Definimos la herramienta de búsqueda
    herramienta_busqueda = Tool.from_google_search_retrieval(
        google_search_retrieval=GoogleSearchRetrieval()
    )
    
    model = GenerativeModel("gemini-1.5-pro") # Versión estable para búsqueda
    prompt = config_prompt.prompt_capa_1_buscador(marca, modelo, anio)
    
    try:
        response = model.generate_content(
            prompt,
            tools=[herramienta_busqueda]
        )
        return response.text
    except Exception as e:
        return f"Error en Capa 1: {str(e)}"
