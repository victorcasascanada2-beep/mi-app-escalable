import streamlit as st
import os
import json
from PIL import Image
from streamlit_js_eval import get_geolocation
import ia_engine

# --- PARCHE DE SECRETOS ---
# Este bloque inyecta tus credenciales de Streamlit Cloud en el entorno
if "GOOGLE_SECRETS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_SECRETS_JSON"])
        st.secrets.update({"google": creds_data})
    except Exception as e:
        st.error(f"Error en credenciales: {e}")

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tasador Agrícola Noroeste", page_icon="🚜", layout="wide")

# Inicialización del Cliente Vertex (Solo una vez)
if "vertex_client" not in st.session_state:
    try:
        # Usamos la función de tu ia_engine con el nuevo SDK
        st.session_state.vertex_client = ia_engine.conectar_vertex(dict(st.secrets["google"]))
    except Exception as e:
        st.error("Configuración de Google Cloud pendiente en los Secrets de Streamlit.")
        st.stop()

if "paso" not in st.session_state:
    st.session_state.paso = 1

# --- GEOLOCALIZACIÓN (Parcheada para evitar NameError) ---
# Eliminamos la llamada a location_manager que no existe
loc = get_geolocation(component_key="gps_capas")
texto_ubica = "Ubicación: Zamora, España (Manual)" # Valor por defecto para pruebas

st.title("🚜 Sistema de Tasación Experta")
st.info("Entorno de Laboratorio: Capas 1 a 4 activas.")

# --- FLUJO POR CAPAS ---

# CAPA 1: BÚSQUEDA DE MERCADO
if st.session_state.paso == 1:
    st.header("1. Análisis de Mercado (Rastreo Real)")
    with st.form("busqueda"):
        col1, col2, col3 = st.columns(3)
        with col1:
            marca = st.text_input("Marca", "Valtra")
        with col2:
            modelo = st.text_input("Modelo", "G125")
        with col3:
            anio = st.number_input("Año", value=2025)
            
        if st.form_submit_button("🔍 BUSCAR REFERENCIAS EN TIEMPO REAL"):
            with st.spinner(f"Gemini 2.5 Pro rastreando anuncios de {marca} {modelo}..."):
                # Llamada al motor con Google Search
                res = ia_engine.buscar_mercado_capa1(st.session_state.vertex_client, marca, modelo, anio)
                st.session_state.anuncios_raw = res
                st.session_state.marca, st.session_state.modelo = marca, modelo
                st.session_state.paso = 2
                st.rerun()

# CAPA 2: FILTRO DE PRECIO Y VALIDACIÓN
elif st.session_state.paso == 2:
    st.header("2. Validación de Precios de Mercado")
    st.subheader(f"Referencias encontradas para {st.session_state.marca} {st.session_state.modelo}:")
    
    # Aquí Gemini muestra la tabla Markdown que definimos en el prompt
    st.markdown(st.session_state.anuncios_raw)
    
    st.divider()
    precio_medio = st.number_input("Establece el Precio Base tras ver las referencias (€):", value=90000)
    
    if st.button("✅ CONFIRMAR PRECIO BASE Y PASAR A PERITAJE"):
        st.session_state.precio_base = precio_medio
        st.session_state.paso = 3
        st.rerun()

# CAPA 3: PERITAJE VISUAL (IA VISION)
elif st.session_state.paso == 3:
    st.header("3. Inspección Visual y Valoración de Extras")
    st.write(f"Trabajando sobre base de: **{st.session_state.precio_base} €**")
    
    col_a, col_b = st.columns(2)
    with col_a:
        obs = st.text_area("Notas sobre el estado o extras (pala, tripuntal, pesas...)")
    with col_b:
        fotos = st.file_uploader("Subir fotos reales del tractor", accept_multiple_files=True)
    
    if st.button("🚀 GENERAR VEREDICTO FINAL"):
        if not fotos:
            st.warning("Se requieren fotos para el análisis visual de la Capa 3.")
        else:
            with st.spinner("Gemini 2.5 Pro analizando imágenes y ajustando precio..."):
                # Capa de visión con optimización de imágenes
                informe = ia_engine.analizar_peritaje_capa3(
                    st.session_state.vertex_client, st.session_state.marca, 
                    st.session_state.modelo, st.session_state.precio_base, 
                    obs, texto_ubica, fotos
                )
                st.session_state.informe_final = informe
                st.session_state.paso = 4
                st.rerun()

# CAPA 4: RESULTADO E INFORME
elif st.session_state.paso == 4:
    st.header("🏁 Informe de Tasación Final")
    st.success("Peritaje completado con éxito.")
    
    st.markdown("---")
    st.markdown(st.session_state.informe_final)
    st.markdown("---")
    
    if st.button("🔄 REALIZAR NUEVA TASACIÓN"):
        st.session_state.paso = 1
        st.rerun()
