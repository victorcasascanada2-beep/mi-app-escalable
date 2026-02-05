import streamlit as st

st.set_page_config(page_title="App Escalable", layout="wide")

st.title("🚀 Mi App para 200 Usuarios")
st.write("Esta aplicación está corriendo en Google Cloud Run y escala automáticamente.")

# Un ejemplo interactivo sencillo
nombre = st.text_input("Introduce tu nombre:")
if nombre:
    st.success(f"¡Hola {nombre}! Bienvenido a la infraestructura elástica.")
