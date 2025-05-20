import streamlit as st
import uuid


def mostrar():
    # --- Estado de la sesión ---
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"session-{uuid.uuid4()}"
    if "inicio" not in st.session_state:
        st.session_state.inicio = True  # mostrar pantalla de inicio

    # --- Estilo personalizado CSS ---
    st.markdown("""
    <style>
        .main-header {
            font-family: 'Helvetica Neue', sans-serif;
            color: #FF69B4;
        }
        .subheader {
            font-family: 'Helvetica Neue', sans-serif;
            color: #808080;
        }
        .service-title {
            font-weight: bold;
            color: #FF69B4;
        }
        .testimonial {
            background-color: #f8f9fa;
            border-left: 4px solid #FF69B4;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Pantalla de bienvenida ---
    if st.session_state.inicio:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("images/logo.jpg", width=250)
        
        with col2:
            st.markdown("<h1 class='main-header'>Little Moments Photography</h1>", unsafe_allow_html=True)
            st.markdown("<h3 class='subheader'>Capturando los primeros momentos de vida con delicadeza y amor</h3>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sección de introducción
        st.markdown("""
        Bienvenidos a **Little Moments Photography**, donde nos especializamos en capturar esos primeros 
        e irrepetibles momentos de la vida de tu bebé. Cada sesión es personalizada para crear recuerdos 
        que atesorarás para siempre.
        """)
        
        # Mostrar servicios en columnas
        st.markdown("<h2 class='main-header'>Nuestros Servicios</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("images/image_1.jpg", caption="Recién Nacidos", use_container_width=True)
            st.markdown("<p class='service-title'>Sesiones para Recién Nacidos</p>", unsafe_allow_html=True)
            st.write("Delicadas sesiones diseñadas para bebés de hasta 15 días de vida.")
        with col2:
            st.image("images/image_2.jpg", caption="Bebés", use_container_width=True)
            st.markdown("<p class='service-title'>Sesiones para Bebés</p>", unsafe_allow_html=True)
            st.write("Capturas los hitos importantes: sentarse, gatear, primeros pasos.")
        with col3:
            st.image("images/image_3.jpg", caption="Smash Cake", use_container_width=True)
            st.markdown("<p class='service-title'>Sesiones Smash Cake</p>", unsafe_allow_html=True)
            st.write("Celebra el primer cumpleaños con una divertida sesión de 'romper el pastel'.")
        
        st.markdown("---")
        
        # Testimonios
        st.markdown("<h2 class='main-header'>Lo Que Dicen Nuestras Familias</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='testimonial'>\"La sesión de fotos con nuestra recién nacida fue una experiencia mágica. Las fotos capturan perfectamente lo pequeña y hermosa que era. ¡Un tesoro para toda la vida!\"<br>- María y Juan, padres de Sofía</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='testimonial'>\"Profesionalismo, paciencia y creatividad. Las fotos de nuestro bebé son espectaculares y el ambiente durante la sesión fue tan relajado que nuestro pequeño dormía plácidamente.\"<br>- Laura, mamá de Lucas</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sección de contacto
        st.markdown("<h2 class='main-header'>Contacto</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            📞 Teléfono: +34 600 123 456  
            📧 Email: info@littlemomentsphotography.com  
            📍 Ubicación: Calle Principal 123, Madrid  
            """)