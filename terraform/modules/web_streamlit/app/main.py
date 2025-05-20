import streamlit as st
from components import sidebar
from pages import web_assitant, web_inicio

st.set_page_config(
    page_title="Little Moments Photography", 
    layout="wide",
    page_icon="👶"
)

# Sidebar para navegar
opcion = sidebar.mostrar_sidebar()

# Navegación entre páginas
if opcion == "Inicio":
    web_inicio.mostrar()
elif opcion == "Asistente":
    web_assitant.mostrar()
