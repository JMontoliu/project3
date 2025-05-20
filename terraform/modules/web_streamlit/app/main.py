import streamlit as st
import requests
import os

# URL de tu API
url = os.getenv("URL_CHATBOT2").rstrip("/")
if not url:
    print("Error: URL_CHATBOT2 no está configurada.")
if not url.endswith("/chat"):
    url += "/chat"

# Configuración de la página
st.set_page_config(page_title="GestorBot de Sarashot", layout="centered")
st.title("GestorBot de Sarashot 📷")
st.title( url )
# Inicializar historial de chat
if "chat" not in st.session_state:
    st.session_state.chat = []  # cada item será un dict con {"role": "user" o "assistant", "message": ...}

# Mostrar historial de mensajes
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["message"])

# Entrada de texto del usuario
user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    # Mostrar el mensaje del usuario
    st.chat_message("user").markdown(user_input)
    st.session_state.chat.append({"role": "user", "message": user_input})

    # Enviar el mensaje a la API
    payload = {
        "thread_id": "ejemplo-python-001",  # puedes cambiar esto según el usuario/sesión
        "message": user_input
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        respuesta = data.get("response", "[Sin respuesta de la API]")

    except requests.exceptions.RequestException as e:
        respuesta = f"❌ Error al conectar con la API:\n{e}"

    # Mostrar la respuesta del chatbot
    st.chat_message("assistant").markdown(respuesta)
    st.session_state.chat.append({"role": "assistant", "message": respuesta})