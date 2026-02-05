import streamlit as st
import os
import json
from PIL import Image
from streamlit_js_eval import get_geolocation
import ia_engine
#import location_manager

# --- PARCHE DE SECRETOS ---
if "GOOGLE_SECRETS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_SECRETS_JSON"])
        st.secrets.update({"google": creds_data})
    except Exception as e:
        st.error(f"Error en credenciales: {e}")

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Tasador Agrícola Noroeste", page_icon="🚜")

# Conexión Segura
if "vertex_client" not in st.session_state:
    try:
        st.session_state.vertex_client = ia_engine.conectar_vertex(dict(st.secrets["google"]))
    except Exception as e:
        st.error("Configuración de Google Cloud pendiente en el panel de Cloud Run.")
        st.stop()

if "paso" not in st.session_state:
    st.session_state.paso = 1

# Geolocalización silenciosa (Arquitectura Dondeestoy)
loc = get_geolocation(component_key="gps_capas")
texto_ubica = location_manager.codificar_coordenadas(loc['coords']['latitude'], loc['coords']['longitude']) if loc else "LOC_PENDIENTE"

st.title("🚜 Sistema de Tasación Experta")

# --- FLUJO POR CAPAS ---

# CAPA 1: BÚSQUEDA
if st.session_state.paso == 1:
    st.header("1. Análisis de Mercado")
    with st.form("busqueda"):
        marca = st.text_input("Marca", "John Deere")
        modelo = st.text_input("Modelo", "6155R")
        anio = st.number_input("Año", value=2018)
        if st.form_submit_button("🔍 BUSCAR REFERENCIAS"):
            with st.spinner("Buscando anuncios reales..."):
                res = ia_engine.buscar_mercado_capa1(st.session_state.vertex_client, marca, modelo, anio)
                st.session_state.anuncios_raw = res
                st.session_state.marca, st.session_state.modelo = marca, modelo
                st.session_state.paso = 2
                st.rerun()

# CAPA 2: FILTRO DE PRECIO
elif st.session_state.paso == 2:
    st.header("2. Validación de Precios")
    st.markdown("### Referencias encontradas por la IA:")
    st.info(st.session_state.anuncios_raw)
    
    precio_medio = st.number_input("Establece el Precio Base tras ver las referencias (€):", value=45000)
    
    if st.button("✅ CONFIRMAR PRECIO Y CONTINUAR"):
        st.session_state.precio_base = precio_medio
        st.session_state.paso = 3
        st.rerun()

# CAPA 3: PERITAJE VISUAL
elif st.session_state.paso == 3:
    st.header("3. Inspección Visual y Extras")
    st.write(f"Trabajando sobre base de: **{st.session_state.precio_base} €**")
    
    obs = st.text_area("Desgaste notable o extras (pala, GPS, pesas...)")
    fotos = st.file_uploader("Subir fotos del estado actual", accept_multiple_files=True)
    
    if st.button("🚀 GENERAR VEREDICTO"):
        if not fotos:
            st.warning("Se requieren fotos para el análisis visual.")
        else:
            with st.spinner("Gemini analizando imágenes..."):
                informe = ia_engine.analizar_peritaje_capa3(
                    st.session_state.vertex_client, st.session_state.marca, 
                    st.session_state.modelo, st.session_state.precio_base, 
                    obs, texto_ubica, fotos
                )
                st.session_state.informe_final = informe
                st.session_state.paso = 4
                st.rerun()

# CAPA FINAL: RESULTADO
elif st.session_state.paso == 4:
    st.header("🏁 Resultado del Peritaje")
    st.markdown(st.session_state.informe_final)
    
    if st.button("🔄 NUEVA CONSULTA"):
        st.session_state.clear()
        st.rerun()