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

if st.session_state.paso == 1:
    st.header("1. Análisis de Mercado (Búsqueda Real)")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1: marca = st.text_input("Marca", "Valtra")
        with c2: modelo = st.text_input("Modelo", "G125")
        with c3: anio = st.number_input("Año", value=2025)
        with c4: horas = st.number_input("Horas actuales", value=0)

        if st.button("🔍 BUSCAR REFERENCIAS"):
            with st.spinner("Rastreando anuncios..."):
                res_list = ia_engine.buscar_mercado_capa1(st.session_state.vertex_client, marca, modelo, anio, horas)
                st.session_state.anuncios_raw = res_list
                st.session_state.marca, st.session_state.modelo = marca, modelo
                st.rerun()

    if "anuncios_raw" in st.session_state:
        st.divider()
        st.subheader("Selecciona los anuncios válidos para la tasación:")
        
        anuncios_finales = []
        # Bucle dinámico: Crea un checkbox por cada anuncio devuelto
        for i, anuncio in enumerate(st.session_state.anuncios_raw):
            # Evitamos mostrar encabezados de tabla o líneas raras
            if "|" in anuncio and "---" not in anuncio and "Portal" not in anuncio:
                if st.checkbox(anuncio, key=f"anuncio_{i}"):
                    anuncios_finales.append(anuncio)
        
        if st.button("🚀 CONFIRMAR SELECCIÓN Y CONTINUAR"):
            if not anuncios_finales:
                st.warning("Selecciona al menos un anuncio para validar el precio.")
            else:
                st.session_state.anuncios_validados = anuncios_finales
                st.session_state.paso = 2
                st.rerun()

elif st.session_state.paso == 2:
    st.header("2. Precio Base")
    st.write(f"Has validado {len(st.session_state.anuncios_validados)} referencias.")
    precio_base = st.number_input("Establece el Precio Base (€):", value=90000)
    if st.button("✅ IR A INSPECCIÓN VISUAL"):
        st.session_state.precio_base = precio_base
        st.session_state.paso = 3
        st.rerun()

elif st.session_state.paso == 3:
    st.header("3. Peritaje y Fotos")
    obs = st.text_area("Notas sobre el estado")
    fotos = st.file_uploader("Subir fotos", accept_multiple_files=True)
    if st.button("🚀 GENERAR INFORME FINAL"):
        with st.spinner("Gemini analizando..."):
            informe = ia_engine.analizar_peritaje_capa3(
                st.session_state.vertex_client, st.session_state.marca, 
                st.session_state.modelo, st.session_state.precio_base, 
                obs, texto_ubica, fotos
            )
            st.session_state.informe_final = informe
            st.session_state.paso = 4
            st.rerun()

elif st.session_state.paso == 4:
    st.header("🏁 Resultado Final")
    st.markdown(st.session_state.informe_final)
    if st.button("🔄 NUEVA TASACIÓN"):
        st.session_state.clear()
        st.rerun()
