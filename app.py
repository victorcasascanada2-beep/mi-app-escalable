import streamlit as st
import os
import json
from PIL import Image
from streamlit_js_eval import get_geolocation
import ia_engine

# --- PARCHE DE SECRETOS ---
if "GOOGLE_SECRETS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_SECRETS_JSON"])
        st.secrets.update({"google": creds_data})
    except Exception as e:
        st.error(f"Error en credenciales: {e}")

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Tasador Agrícola Noroeste", page_icon="🚜", layout="wide")

if "vertex_client" not in st.session_state:
    try:
        st.session_state.vertex_client = ia_engine.conectar_vertex(dict(st.secrets["google"]))
    except Exception as e:
        st.error("Configuración de Google Cloud pendiente.")
        st.stop()

if "paso" not in st.session_state:
    st.session_state.paso = 1

texto_ubica = "Zamora, España"

st.title("🚜 Sistema de Tasación Experta")

# --- FLUJO POR CAPAS ---

# CAPA 1: BÚSQUEDA Y FILTRADO POR HORAS
if st.session_state.paso == 1:
    st.header("1. Análisis de Mercado y Selección")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1: marca = st.text_input("Marca", "Valtra")
        with col2: modelo = st.text_input("Modelo", "G125")
        with col3: anio = st.number_input("Año", value=2025)
        with col4: horas = st.number_input("Horas actuales", value=0)

        if st.button("🔍 BUSCAR REFERENCIAS"):
            with st.spinner(f"Buscando {marca} con {horas}h..."):
                # Enviamos las 5 variables necesarias
                res = ia_engine.buscar_mercado_capa1(st.session_state.vertex_client, marca, modelo, anio, horas)
                st.session_state.anuncios_raw = res
                st.session_state.marca, st.session_state.modelo = marca, modelo
                st.session_state.paso_sub = "seleccion"
                st.rerun()

    if "anuncios_raw" in st.session_state:
        st.divider()
        st.markdown(st.session_state.anuncios_raw)
        
        # Filtro Booleano sencillo
        opciones = ["Referencia 1", "Referencia 2", "Referencia 3", "Referencia 4"]
        seleccionados = st.multiselect("Selecciona las que entrarán en la media:", opciones, default=opciones[:2])
        
        if st.button("🚀 CONFIRMAR SELECCIÓN"):
            st.session_state.paso = 2
            st.rerun()

# CAPA 2: VALIDACIÓN DE PRECIO
elif st.session_state.paso == 2:
    st.header("2. Precio Base de Mercado")
    precio_medio = st.number_input("Establece el Precio Base (€):", value=90000)
    if st.button("✅ IR AL PERITAJE"):
        st.session_state.precio_base = precio_medio
        st.session_state.paso = 3
        st.rerun()

# CAPA 3: PERITAJE VISUAL
elif st.session_state.paso == 3:
    st.header("3. Inspección Visual")
    obs = st.text_area("Notas del estado")
    fotos = st.file_uploader("Fotos", accept_multiple_files=True)
    if st.button("🚀 GENERAR INFORME"):
        with st.spinner("Analizando..."):
            informe = ia_engine.analizar_peritaje_capa3(
                st.session_state.vertex_client, st.session_state.marca, 
                st.session_state.modelo, st.session_state.precio_base, 
                obs, texto_ubica, fotos
            )
            st.session_state.informe_final = informe
            st.session_state.paso = 4
            st.rerun()

# CAPA 4: RESULTADO
elif st.session_state.paso == 4:
    st.header("🏁 Informe Final")
    st.markdown(st.session_state.informe_final)
    if st.button("🔄 NUEVA CONSULTA"):
        st.session_state.clear()
        st.rerun()
