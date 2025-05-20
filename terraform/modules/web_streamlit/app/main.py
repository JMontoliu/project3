import streamlit as st
import requests
import os
import uuid

# URL de tu API
url = os.getenv("URL_CHATBOT2").rstrip("/")
if not url:
    print("Error: URL_CHATBOT2 no está configurada.")
if not url.endswith("/chat"):
    url += "/chat"

# Configuración de la página
st.set_page_config(page_title="GestorBot de Sarashot", layout="centered")
st.title("GestorBot de Sarashot 📷")

# --- Estado de sesión ---
if "chat" not in st.session_state:
    st.session_state.chat = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session-{uuid.uuid4()}"

# --- Función para enviar mensaje a la API ---
def send_message_to_api(user_input):
    payload = {
        "thread_id": st.session_state.thread_id,
        "message": user_input
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "⚠️ No se recibió respuesta del servidor.")
    except requests.exceptions.RequestException as e:
        return f"❌ Error al conectar con la API:\n`{str(e)}`"

# --- Mostrar historial ---
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["message"])

# --- Entrada de texto del usuario ---
user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    # Mostrar el mensaje del usuario
    st.chat_message("user").markdown(user_input)
    st.session_state.chat.append({"role": "user", "message": user_input})

    with st.spinner("Pensando..."):
        respuesta = send_message_to_api(user_input)

    # Mostrar la respuesta del asistente
    st.chat_message("assistant").markdown(respuesta)
    st.session_state.chat.append({"role": "assistant", "message": respuesta})