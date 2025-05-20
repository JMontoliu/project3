import streamlit as st
import requests
import os
import uuid
from urllib.parse import urljoin
import time

def mostrar():
    # --- Estilo personalizado CSS ---
    st.markdown("""
    <style>
        .main-header {
            font-family: 'Helvetica Neue', sans-serif;
            color: #FF69B4;
            text-align: center;
        }
        .subheader {
            font-family: 'Helvetica Neue', sans-serif;
            color: #808080;
            text-align: center;
        }
        .stChatMessage {
            border-radius: 15px;
        }
        div.stChatMessage [data-testid="StChatMessageContent"] {
            background-color: #f7f7f7;
            border-radius: 15px;
        }
        div.stChatMessage.assistant [data-testid="StChatMessageContent"] {
            background-color: #FFF0F5;
        }
        .info-box {
            background-color: #FFF0F5;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid #FFD1DC;
        }
        .contact-button {
            background-color: #FF69B4;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
            text-align: center;
            margin: 10px 0;
            cursor: pointer;
        }
        .back-button {
            background-color: #f0f0f0;
            color: #333;
            border-radius: 5px;
            padding: 5px 15px;
            font-size: 14px;
            cursor: pointer;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Título y logotipo ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='main-header'>BabyBot</h1>", unsafe_allow_html=True)
        st.markdown("<h3 class='subheader'>Asistente de Little Moments Photography</h3>", unsafe_allow_html=True)

    # --- Estado de sesión ---
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"session-{uuid.uuid4()}"

    if "bienvenida_mostrada" not in st.session_state:
        st.session_state.bienvenida_mostrada = False

    # --- Mensaje de bienvenida inicial ---
    if not st.session_state.bienvenida_mostrada:
        bienvenida = """
        👋 ¡Hola! Soy BabyBot, el asistente virtual de Little Moments Photography.
        
        Puedo ayudarte con:
        - Información sobre nuestras sesiones para recién nacidos, bebés y Smash Cake
        - Detalles sobre precios y paquetes disponibles
        - Cómo prepararte para una sesión fotográfica
        - Reservar una cita para tu bebé
        
        ¿En qué puedo ayudarte hoy?
        """
        st.session_state.chat.append({"role": "assistant", "message": bienvenida})
        st.session_state.bienvenida_mostrada = True

    # --- Mostrar historial de chat ---
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["message"])

    # --- Información de contacto en el sidebar ---
    with st.sidebar:
        st.markdown("### Little Moments Photography")
        
        st.markdown("#### Contacto")
        st.markdown("""
        📞 +34 600 123 456  
        📧 info@littlemoments.com  
        📍 Calle Principal 123, Madrid
        """)
        
        st.markdown("#### Horario")
        st.markdown("""
        Lunes - Viernes: 9:00 - 19:00  
        Sábados: 10:00 - 14:00  
        Domingos: Cerrado
        """)
        
        # Botón para volver a la página principal
        if st.button("← Volver a la página principal", key="sidebar_back"):
            st.session_state.inicio = True
            st.experimental_rerun()

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

    # --- Información adicional al final ---
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
    <strong>¿Prefieres hablar directamente con nosotros?</strong><br>
    Llámanos al +34 600 123 456 o envíanos un email a info@littlemoments.com para agendar una consulta personalizada.
    </div>
    """, unsafe_allow_html=True)

# --- Función para enviar mensaje a la API ---
def send_message_to_api(user_input):

    # URL de tu API
    url = os.getenv("URL_CHATBOT2").rstrip("/")
    if not url:
        print("Error: URL_CHATBOT2 no está configurada.")
    if not url.endswith("/chat"):
        url += "/chat"
    
    payload = {
        "thread_id": st.session_state.thread_id,
        "message": user_input
    }
    
    # Lista de respuestas preprogramadas basadas en palabras clave
    keyword_responses = {
        "precio": "Nuestros paquetes para fotografía de bebés comienzan desde 150€ e incluyen:\n\n- Sesión de 1-2 horas\n- 10 fotografías digitales editadas\n- 5 impresiones en formato 15x20cm\n\nTambién ofrecemos paquetes personalizados. ¿Te gustaría más detalles sobre algún servicio específico?",
        
        "cita": "Para agendar una sesión fotográfica, necesitamos planificarla con anticipación, especialmente para recién nacidos. Te recomendamos contactarnos durante tu embarazo para reservar una fecha tentativa. ¿Te gustaría que te contacte nuestra fotógrafa para coordinar los detalles?",
        
        "recién nacido": "Nuestras sesiones para recién nacidos son ideales durante los primeros 15 días de vida cuando el bebé es más flexible y duerme profundamente. La sesión dura aproximadamente 2-3 horas, permitiendo tiempo para alimentación y descansos. ¿Te gustaría conocer cómo prepararte para una sesión de recién nacido?",
        
        "smash cake": "¡Las sesiones Smash Cake son muy divertidas! Diseñadas para celebrar el primer cumpleaños, incluyen una pequeña tarta especialmente preparada para que el bebé juegue y la 'destroce'. Proporcionamos el escenario, la tarta y la limpieza posterior. ¡Solo necesitas traer a tu pequeño y tu cámara para capturar su expresión!",
        
        "ubicación": "Nuestro estudio está ubicado en Calle Principal 123, Madrid. Contamos con un espacio acogedor, temperatura controlada y todas las comodidades para ti y tu bebé. También ofrecemos sesiones a domicilio o en exteriores según el tipo de fotografía que prefieras.",
        
        "preparación": "Para preparar a tu bebé para una sesión fotográfica, recomendamos:\n\n- Alimentarlo justo antes de la sesión\n- Traer su manta o juguete favorito\n- Ropa extra en caso de accidentes\n- Para recién nacidos, mantenerlos despiertos 1-2 horas antes para que duerman durante la sesión\n\n¿Hay algo específico que te preocupe sobre la preparación?"
    }

    # Buscar palabras clave en el mensaje del usuario
    for keyword, response in keyword_responses.items():
        if keyword in user_input.lower():
            # Simular el retraso de una API
            time.sleep(1.5)
            return response
    
    try:
        # Si no hay palabras clave coincidentes, enviar a la API real
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "Disculpa, estoy teniendo problemas para procesar tu solicitud. ¿Podrías intentar con otra pregunta?")
    except requests.exceptions.RequestException:
        # En caso de error con la API, enviar una respuesta genérica
        return "Gracias por tu mensaje. Actualmente nuestro sistema está experimentando dificultades. ¿Te gustaría que un miembro de nuestro equipo te contacte directamente? Puedes llamarnos también al +34 600 123 456."
