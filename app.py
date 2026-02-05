import streamlit as st
from PIL import Image
from streamlit_js_eval import get_geolocation
import ia_engine
import location_manager

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="Tasador Pro Capas", page_icon="🚜")

if "paso" not in st.session_state:
    st.session_state.paso = 1
if "vertex_client" not in st.session_state:
    st.session_state.vertex_client = ia_engine.conectar_vertex(dict(st.secrets["google"]))

# Ubicación (Arquitectura Dondeestoy)
loc = get_geolocation(component_key="gps_capas")
texto_ubica = location_manager.codificar_coordenadas(loc['coords']['latitude'], loc['coords']['longitude']) if loc else "LOC_PENDIENTE"

st.title("🚜 Tasación Profesional por Capas")

# 2. CAPA 1: EL BUSCADOR
if st.session_state.paso == 1:
    st.header("Capa 1: Búsqueda de Mercado")
    with st.form("busqueda"):
        marca = st.text_input("Marca", "John Deere")
        modelo = st.text_input("Modelo", "6155R")
        anio = st.number_input("Año", value=2018)
        if st.form_submit_button("🔍 BUSCAR ANUNCIOS"):
            with st.spinner("Buscando en portales europeos..."):
                res = ia_engine.buscar_mercado_capa1(st.session_state.vertex_client, marca, modelo, anio)
                st.session_state.anuncios_raw = res
                st.session_state.marca = marca
                st.session_state.modelo = modelo
                st.session_state.paso = 2
                st.rerun()

# 3. CAPA 2: EL FILTRO (LA MEDIA TRUNCADA)
elif st.session_state.paso == 2:
    st.header("Capa 2: Validación de Datos")
    st.markdown(st.session_state.anuncios_raw)
    
    precio_medio = st.number_input("Tras ver los anuncios, indica el Precio Base (Media Truncada):", value=50000)
    
    if st.button("✅ CONFIRMAR PRECIO BASE"):
        st.session_state.precio_base = precio_medio
        st.session_state.paso = 3
        st.rerun()

# 4. CAPA 3: EL PERITO (VISIÓN Y EXTRAS)
elif st.session_state.paso == 3:
    st.header("Capa 3: Peritaje Visual y Ajustes")
    observaciones = st.text_area("Notas sobre el estado/extras")
    fotos = st.file_uploader("Fotos del tractor", accept_multiple_files=True)
    
    if st.button("🚀 FINALIZAR TASACIÓN"):
        with st.spinner("Analizando fotos y calculando ajustes..."):
            informe = ia_engine.analizar_peritaje_capa3(
                st.session_state.vertex_client, st.session_state.marca, 
                st.session_state.modelo, st.session_state.precio_base, 
                observaciones, texto_ubica, fotos
            )
            st.session_state.informe_final = informe
            st.session_state.paso = 4
            st.rerun()

# 5. RESULTADO FINAL
elif st.session_state.paso == 4:
    st.success("Veredicto Final")
    st.markdown(st.session_state.informe_final)
    if st.button("🔄 NUEVA TASACIÓN"):
        st.session_state.clear()
        st.rerun()
