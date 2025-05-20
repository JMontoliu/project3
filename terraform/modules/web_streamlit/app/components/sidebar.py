import streamlit as st

def mostrar_sidebar():
    st.sidebar.title("Navegación")
    return st.sidebar.selectbox("Ir a:", ["Inicio", "Asistente"])
