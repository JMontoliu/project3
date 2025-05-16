import streamlit as st
import pandas as pd
import re
from datetime import date, time

# Configuración de la página
st.set_page_config(
    page_title="Registro y Modificación de Autónomos",
    page_icon="👷‍♂️",
    layout="wide"
)

# Función para validar DNI/NIE español
def validar_dni_nie(dni):
    # Patrones para DNI y NIE
    patron_dni = r'^[0-9]{8}[A-Za-z]$'
    patron_nie = r'^[XYZxyz][0-9]{7}[A-Za-z]$'
    
    if re.match(patron_dni, dni) or re.match(patron_nie, dni):
        return True
    return False

# Función para validar formato de email
def validar_email(email):
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron_email, email):
        return True
    return False

# Función para validar teléfono español (9 dígitos)
def validar_telefono(telefono):
    patron_telefono = r'^[6-9][0-9]{8}$'
    if re.match(patron_telefono, telefono):
        return True
    return False

# Función para eliminar un autónomo
def eliminar_autonomo(id_autonomo):
    for i, autonomo in enumerate(st.session_state.autonomos_registrados):
        if autonomo["ID"] == id_autonomo:
            del st.session_state.autonomos_registrados[i]
            return True
    return False

# Título principal
st.title("📝 Registro y Modificación de Autónomos")
st.markdown("Complete la información para registrar un nuevo autónomo o modificar uno existente.")

# Inicializar variables de estado en session_state si no existen
if 'formulario_valido' not in st.session_state:
    st.session_state.formulario_valido = True
if 'errores' not in st.session_state:
    st.session_state.errores = {}
if 'datos_personales' not in st.session_state:
    st.session_state.datos_personales = {
        'nombre': "",
        'apellido': "",
        'dni': "",
        'fecha_nacimiento': date.today(),
        'categoria': "Seleccione una categoría",
        'email': "",
        'telefono': "",
        'provincia': "Seleccione una provincia"
    }
if 'disponibilidad' not in st.session_state:
    st.session_state.disponibilidad = {
        'lunes': False,
        'martes': False,
        'miercoles': False,
        'jueves': False,
        'viernes': False,
        'sabado': False,
        'domingo': False,
        'hora_inicio': time(9, 0),
        'hora_fin': time(18, 0)
    }
if 'contador_autonomos' not in st.session_state:
    st.session_state.contador_autonomos = 0
if 'autonomos_registrados' not in st.session_state:
    st.session_state.autonomos_registrados = []
if 'autonomo_seleccionado' not in st.session_state:
    st.session_state.autonomo_seleccionado = None
if 'admin_autenticado' not in st.session_state:
    st.session_state.admin_autenticado = False

# Función para generar un ID único para el autónomo
def generar_id_autonomo():
    st.session_state.contador_autonomos += 1
    prefijo = "AUT"
    numero = str(st.session_state.contador_autonomos).zfill(4)  # Rellena con ceros a la izquierda
    return f"{prefijo}-{numero}"

# Función para reiniciar el formulario
def reiniciar_formulario():
    st.session_state.datos_personales = {
        'nombre': "",
        'apellido': "",
        'dni': "",
        'fecha_nacimiento': date.today(),
        'categoria': "Seleccione una categoría",
        'email': "",
        'telefono': "",
        'provincia': "Seleccione una provincia"
    }
    st.session_state.disponibilidad = {
        'lunes': False,
        'martes': False,
        'miercoles': False,
        'jueves': False,
        'viernes': False,
        'sabado': False,
        'domingo': False,
        'hora_inicio': time(9, 0),
        'hora_fin': time(18, 0)
    }
    st.session_state.formulario_valido = True
    st.session_state.errores = {}
    st.session_state.autonomo_seleccionado = None

# Función para buscar un autónomo por DNI
def buscar_autonomo_por_dni(dni):
    for autonomo in st.session_state.autonomos_registrados:
        if autonomo["DNI/NIE"] == dni:
            return autonomo
    return None

# Función para actualizar un autónomo
def actualizar_autonomo(autonomo_actualizado):
    for i, autonomo in enumerate(st.session_state.autonomos_registrados):
        if autonomo["ID"] == autonomo_actualizado["ID"]:
            st.session_state.autonomos_registrados[i] = autonomo_actualizado
            return True
    return False

# Crear una sección para mostrar los autónomos registrados (opcional)
if st.session_state.autonomos_registrados:
    with st.expander("Ver autónomos registrados", expanded=False):
        st.subheader(f"Autónomos Registrados ({len(st.session_state.autonomos_registrados)})")
        
        for i, autonomo in enumerate(st.session_state.autonomos_registrados):
            with st.container():
                st.markdown(f"**{autonomo['ID']} - {autonomo['Nombre completo']}**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Categoría: {autonomo['Categoría']}")
                    st.write(f"Provincia: {autonomo['Provincia']}")
                with col2:
                    st.write(f"Días: {autonomo['Días disponibles']}")
                    st.write(f"Horario: {autonomo['Horario']}")
                st.divider()

# Crear pestañas
tab_labels = ["Información Personal y Profesional", "Disponibilidad", "Modificar Disponibilidad", "Administración"]
tabs = st.tabs(tab_labels)

# Pestaña 1: Información Personal y Profesional
with tabs[0]:
    st.subheader("Información Personal")
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input(
            "Nombre", 
            value=st.session_state.datos_personales['nombre'],
            placeholder="Ej: Juan"
        )
        st.session_state.datos_personales['nombre'] = nombre
        if not st.session_state.formulario_valido and "nombre" in st.session_state.errores:
            st.error(st.session_state.errores["nombre"])
    
    with col2:
        apellido = st.text_input(
            "Apellidos", 
            value=st.session_state.datos_personales['apellido'],
            placeholder="Ej: García López"
        )
        st.session_state.datos_personales['apellido'] = apellido
        if not st.session_state.formulario_valido and "apellido" in st.session_state.errores:
            st.error(st.session_state.errores["apellido"])
    
    dni = st.text_input(
        "DNI/NIE", 
        value=st.session_state.datos_personales['dni'],
        placeholder="Ej: 12345678A", 
        max_chars=9,
        help="Introduzca 8 números seguidos de una letra (DNI) o letra+7 números+letra (NIE)"
    )
    st.session_state.datos_personales['dni'] = dni
    if not st.session_state.formulario_valido and "dni" in st.session_state.errores:
        st.error(st.session_state.errores["dni"])
    
    fecha_nacimiento = st.date_input(
        "Fecha de Nacimiento", 
        value=st.session_state.datos_personales['fecha_nacimiento'],
        min_value=date(1940, 1, 1),
        max_value=date.today()
    )
    st.session_state.datos_personales['fecha_nacimiento'] = fecha_nacimiento
    
    st.subheader("Información Profesional")
    
    # Lista de categorías profesionales
    categorias = [
        "Seleccione una categoría",
        "Fotografía",
        "Fontanería",
        "Mecánica",
        "Electricidad",
        "Carpintería",
        "Diseño gráfico",
        "Pintura",
        "Jardinería",
        "Peluquería",
        "Asesoría"
    ]
    
    categoria = st.selectbox(
        "Categoría profesional", 
        options=categorias,
        index=categorias.index(st.session_state.datos_personales['categoria'])
    )
    st.session_state.datos_personales['categoria'] = categoria
    if not st.session_state.formulario_valido and "categoria" in st.session_state.errores:
        st.error(st.session_state.errores["categoria"])
    
    email = st.text_input(
        "Email", 
        value=st.session_state.datos_personales['email'],
        placeholder="ejemplo@correo.com"
    )
    st.session_state.datos_personales['email'] = email
    if not st.session_state.formulario_valido and "email" in st.session_state.errores:
        st.error(st.session_state.errores["email"])
    
    telefono = st.text_input(
        "Teléfono", 
        value=st.session_state.datos_personales['telefono'],
        placeholder="Ej: 612345678", 
        max_chars=9
    )
    st.session_state.datos_personales['telefono'] = telefono
    if not st.session_state.formulario_valido and "telefono" in st.session_state.errores:
        st.error(st.session_state.errores["telefono"])
    
    # Lista de provincias españolas
    provincias = [
        "Seleccione una provincia",
        "Álava", "Albacete", "Alicante", "Almería", "Asturias",
        "Ávila", "Badajoz", "Barcelona", "Bizkaia", "Burgos",
        "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real",
        "Córdoba", "A Coruña", "Cuenca", "Girona", "Granada",
        "Guadalajara", "Gipuzkoa", "Huelva", "Huesca", "Illes Balears",
        "Jaén", "León", "Lleida", "Lugo", "Madrid",
        "Málaga", "Murcia", "Navarra", "Ourense", "Palencia",
        "Las Palmas", "Pontevedra", "La Rioja", "Salamanca", "Santa Cruz de Tenerife",
        "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel",
        "Toledo", "Valencia", "Valladolid", "Zamora", "Zaragoza"
    ]
    
    provincia = st.selectbox(
        "Provincia", 
        options=provincias,
        index=provincias.index(st.session_state.datos_personales['provincia'])
    )
    st.session_state.datos_personales['provincia'] = provincia
    if not st.session_state.formulario_valido and "provincia" in st.session_state.errores:
        st.error(st.session_state.errores["provincia"])
    
    # Instrucción para el usuario
    st.info("Complete la información y luego vaya a la pestaña 'Disponibilidad' para finalizar el registro.")

# Pestaña 2: Disponibilidad
with tabs[1]:
    st.subheader("Días y Horarios de Trabajo")
    st.write("Seleccione los días en los que está disponible para trabajar y su horario preferido.")
    
    # Selección de días de la semana
    st.write("**Días disponibles:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lunes = st.checkbox("Lunes", value=st.session_state.disponibilidad['lunes'])
        st.session_state.disponibilidad['lunes'] = lunes
        
        martes = st.checkbox("Martes", value=st.session_state.disponibilidad['martes'])
        st.session_state.disponibilidad['martes'] = martes
    
    with col2:
        miercoles = st.checkbox("Miércoles", value=st.session_state.disponibilidad['miercoles'])
        st.session_state.disponibilidad['miercoles'] = miercoles
        
        jueves = st.checkbox("Jueves", value=st.session_state.disponibilidad['jueves'])
        st.session_state.disponibilidad['jueves'] = jueves
    
    with col3:
        viernes = st.checkbox("Viernes", value=st.session_state.disponibilidad['viernes'])
        st.session_state.disponibilidad['viernes'] = viernes
        
        sabado = st.checkbox("Sábado", value=st.session_state.disponibilidad['sabado'])
        st.session_state.disponibilidad['sabado'] = sabado
    
    with col4:
        domingo = st.checkbox("Domingo", value=st.session_state.disponibilidad['domingo'])
        st.session_state.disponibilidad['domingo'] = domingo
    
    # Selección de horario
    st.write("**Horario de trabajo:**")
    col1, col2 = st.columns(2)
    
    with col1:
        hora_inicio = st.time_input(
            "Hora de inicio", 
            value=st.session_state.disponibilidad['hora_inicio']
        )
        st.session_state.disponibilidad['hora_inicio'] = hora_inicio
    
    with col2:
        hora_fin = st.time_input(
            "Hora de fin", 
            value=st.session_state.disponibilidad['hora_fin']
        )
        st.session_state.disponibilidad['hora_fin'] = hora_fin
    
    # Validación del horario
    if hora_fin <= hora_inicio:
        st.error("La hora de fin debe ser posterior a la hora de inicio")
        puede_registrar = False
    else:
        puede_registrar = True
    
    # Validación de al menos un día seleccionado
    dias_seleccionados = [
        lunes, martes, miercoles, jueves, viernes, sabado, domingo
    ]
    
    if not any(dias_seleccionados):
        st.error("Debe seleccionar al menos un día de disponibilidad")
        puede_registrar = False
    
    # Verificar que la información personal está completa
    datos_completos = (
        st.session_state.datos_personales['nombre'] and
        st.session_state.datos_personales['apellido'] and
        st.session_state.datos_personales['dni'] and
        validar_dni_nie(st.session_state.datos_personales['dni']) and
        st.session_state.datos_personales['categoria'] != "Seleccione una categoría" and
        st.session_state.datos_personales['email'] and
        validar_email(st.session_state.datos_personales['email']) and
        st.session_state.datos_personales['telefono'] and
        validar_telefono(st.session_state.datos_personales['telefono']) and
        st.session_state.datos_personales['provincia'] != "Seleccione una provincia"
    )
    
    if not datos_completos:
        st.warning("Complete primero la información personal y profesional en la pestaña anterior")
        puede_registrar = False
    
    # Botón de registro final
    if puede_registrar:
        if st.button("Registrar Autónomo"):
            # Comprobar si el DNI ya existe
            dni_existente = False
            for autonomo in st.session_state.autonomos_registrados:
                if autonomo["DNI/NIE"] == dni:
                    dni_existente = True
                    break
            
            if dni_existente:
                st.error(f"Ya existe un autónomo registrado con el DNI/NIE {dni}")
            else:
                # Generar ID único para el autónomo
                id_autonomo = generar_id_autonomo()
                
                # Preparar los datos para mostrar
                dias_disponibles = []
                if lunes: dias_disponibles.append("Lunes")
                if martes: dias_disponibles.append("Martes")
                if miercoles: dias_disponibles.append("Miércoles")
                if jueves: dias_disponibles.append("Jueves")
                if viernes: dias_disponibles.append("Viernes")
                if sabado: dias_disponibles.append("Sábado")
                if domingo: dias_disponibles.append("Domingo")
                
                # Formatear horario
                horario = f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"
                
                # Crear un diccionario con los datos personales
                datos_personales = {
                    "ID": id_autonomo,
                    "Nombre completo": f"{st.session_state.datos_personales['nombre']} {st.session_state.datos_personales['apellido']}",
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "DNI/NIE": dni,
                    "Fecha de nacimiento": fecha_nacimiento.strftime("%d/%m/%Y"),
                    "Categoría": categoria,
                    "Email": email,
                    "Teléfono": telefono,
                    "Provincia": provincia
                }
                
                # Crear un diccionario con los datos de disponibilidad
                datos_disponibilidad = {
                    "Días disponibles": ", ".join(dias_disponibles),
                    "Días": {
                        "Lunes": lunes,
                        "Martes": martes,
                        "Miércoles": miercoles,
                        "Jueves": jueves,
                        "Viernes": viernes,
                        "Sábado": sabado,
                        "Domingo": domingo
                    },
                    "Hora inicio": hora_inicio,
                    "Hora fin": hora_fin,
                    "Horario": horario
                }
                
                # Combinar todos los datos
                datos_completos = {**datos_personales, **datos_disponibilidad}
                
                # Guardar el autónomo en la lista de registrados
                st.session_state.autonomos_registrados.append(datos_completos)
                
                # Mostrar mensaje de éxito
                st.success(f"¡Autónomo registrado con éxito! ID asignado: {id_autonomo}")
                
                # Mostrar los datos registrados
                st.subheader("Datos registrados")
                
                # Convertir a DataFrame para mejor visualización
                datos_mostrar = {
                    "ID": id_autonomo,
                    "Nombre completo": datos_completos["Nombre completo"],
                    "DNI/NIE": datos_completos["DNI/NIE"],
                    "Fecha de nacimiento": datos_completos["Fecha de nacimiento"],
                    "Categoría": datos_completos["Categoría"],
                    "Email": datos_completos["Email"],
                    "Teléfono": datos_completos["Teléfono"],
                    "Provincia": datos_completos["Provincia"],
                    "Días disponibles": datos_completos["Días disponibles"],
                    "Horario": datos_completos["Horario"]
                }
                
                df = pd.DataFrame(list(datos_mostrar.items()), columns=["Campo", "Valor"])
                st.dataframe(df, use_container_width=True)
                
                # Nota sobre la conexión a GCP
                st.info("La conexión a la base de datos de GCP se implementará en una fase posterior.")
                
                # Reiniciar el formulario para un nuevo registro
                reiniciar_formulario()
                
                # Mostrar un botón para registrar otro autónomo
                if st.button("Registrar otro autónomo"):
                    st.rerun()

# Pestaña 3: Modificar Disponibilidad
with tabs[2]:
    st.subheader("Modificar Disponibilidad de un Autónomo Existente")
    st.markdown("Introduzca el DNI/NIE del autónomo cuya disponibilidad desea modificar.")
    
    # Búsqueda por DNI
    dni_busqueda = st.text_input(
        "DNI/NIE del autónomo", 
        placeholder="Ej: 12345678A",
        help="Introduzca el DNI/NIE exactamente como fue registrado"
    )
    
    # Botón de búsqueda
    if st.button("Buscar Autónomo"):
        if not dni_busqueda:
            st.error("Por favor, introduzca un DNI/NIE para buscar")
        else:
            autonomo = buscar_autonomo_por_dni(dni_busqueda)
            if autonomo:
                st.session_state.autonomo_seleccionado = autonomo
                st.success(f"Autónomo encontrado: {autonomo['Nombre completo']}")
            else:
                st.error(f"No se encontró ningún autónomo con DNI/NIE: {dni_busqueda}")
                st.session_state.autonomo_seleccionado = None
    
    # Mostrar formulario de edición si hay un autónomo seleccionado
    if st.session_state.autonomo_seleccionado:
        st.subheader(f"Editar disponibilidad de {st.session_state.autonomo_seleccionado['Nombre completo']}")
        
        # Extraer información del autónomo seleccionado
        autonomo = st.session_state.autonomo_seleccionado
        
        # Mostrar información básica (no editable)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**ID:** {autonomo['ID']}")
            st.write(f"**Nombre:** {autonomo['Nombre completo']}")
            st.write(f"**DNI/NIE:** {autonomo['DNI/NIE']}")
        with col2:
            st.write(f"**Categoría:** {autonomo['Categoría']}")
            st.write(f"**Provincia:** {autonomo['Provincia']}")
            st.write(f"**Email:** {autonomo['Email']}")
        
        st.divider()
        
        # Selección de días de la semana
        st.write("**Días disponibles:**")
        col1, col2, col3, col4 = st.columns(4)
        
        dias_actuales = autonomo.get("Días", {})
        
        with col1:
            lunes_edit = st.checkbox("Lunes", value=dias_actuales.get("Lunes", False), key="edit_lunes")
            martes_edit = st.checkbox("Martes", value=dias_actuales.get("Martes", False), key="edit_martes")
        
        with col2:
            miercoles_edit = st.checkbox("Miércoles", value=dias_actuales.get("Miércoles", False), key="edit_miercoles")
            jueves_edit = st.checkbox("Jueves", value=dias_actuales.get("Jueves", False), key="edit_jueves")
        
        with col3:
            viernes_edit = st.checkbox("Viernes", value=dias_actuales.get("Viernes", False), key="edit_viernes")
            sabado_edit = st.checkbox("Sábado", value=dias_actuales.get("Sábado", False), key="edit_sabado")
        
        with col4:
            domingo_edit = st.checkbox("Domingo", value=dias_actuales.get("Domingo", False), key="edit_domingo")
        
        # Selección de horario
        st.write("**Horario de trabajo:**")
        col1, col2 = st.columns(2)
        
        with col1:
            hora_inicio_edit = st.time_input(
                "Hora de inicio", 
                value=autonomo.get("Hora inicio", time(9, 0)),
                key="edit_hora_inicio"
            )
        
        with col2:
            hora_fin_edit = st.time_input(
                "Hora de fin", 
                value=autonomo.get("Hora fin", time(18, 0)),
                key="edit_hora_fin"
            )
        
        # Validación del horario
        if hora_fin_edit <= hora_inicio_edit:
            st.error("La hora de fin debe ser posterior a la hora de inicio")
            puede_actualizar = False
        else:
            puede_actualizar = True
        
        # Validación de al menos un día seleccionado
        dias_seleccionados_edit = [
            lunes_edit, martes_edit, miercoles_edit, jueves_edit, 
            viernes_edit, sabado_edit, domingo_edit
        ]
        
        if not any(dias_seleccionados_edit):
            st.error("Debe seleccionar al menos un día de disponibilidad")
            puede_actualizar = False
        
        # Botón para actualizar
        if puede_actualizar:
            if st.button("Actualizar Disponibilidad"):
                # Preparar los datos para mostrar
                dias_disponibles_edit = []
                if lunes_edit: dias_disponibles_edit.append("Lunes")
                if martes_edit: dias_disponibles_edit.append("Martes")
                if miercoles_edit: dias_disponibles_edit.append("Miércoles")
                if jueves_edit: dias_disponibles_edit.append("Jueves")
                if viernes_edit: dias_disponibles_edit.append("Viernes")
                if sabado_edit: dias_disponibles_edit.append("Sábado")
                if domingo_edit: dias_disponibles_edit.append("Domingo")
                
                # Formatear horario
                horario_edit = f"{hora_inicio_edit.strftime('%H:%M')} - {hora_fin_edit.strftime('%H:%M')}"
                
                # Actualizar los datos de disponibilidad
                autonomo_actualizado = autonomo.copy()
                autonomo_actualizado["Días disponibles"] = ", ".join(dias_disponibles_edit)
                autonomo_actualizado["Días"] = {
                    "Lunes": lunes_edit,
                    "Martes": martes_edit,
                    "Miércoles": miercoles_edit,
                    "Jueves": jueves_edit,
                    "Viernes": viernes_edit,
                    "Sábado": sabado_edit,
                    "Domingo": domingo_edit
                }
                autonomo_actualizado["Hora inicio"] = hora_inicio_edit
                autonomo_actualizado["Hora fin"] = hora_fin_edit
                autonomo_actualizado["Horario"] = horario_edit
                
                # Actualizar el autónomo en la lista
                if actualizar_autonomo(autonomo_actualizado):
                    st.success("¡Disponibilidad actualizada con éxito!")
                    
                    # Actualizar el autónomo seleccionado
                    st.session_state.autonomo_seleccionado = autonomo_actualizado
                    
                    # Mostrar los datos actualizados
                    st.subheader("Datos actualizados")
                    
                    # Crear un dataframe para mostrar
                    datos_mostrar = {
                        "ID": autonomo_actualizado["ID"],
                        "Nombre completo": autonomo_actualizado["Nombre completo"],
                        "Días disponibles": autonomo_actualizado["Días disponibles"],
                        "Horario": autonomo_actualizado["Horario"]
                    }
                    
                    df = pd.DataFrame(list(datos_mostrar.items()), columns=["Campo", "Valor"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Error al actualizar la disponibilidad")

# Función para verificar credenciales de administrador
def verificar_admin(usuario, contraseña):
    # Sustituye estas credenciales por las reales
    admin_credenciales = {
        "admin": "admin123"  # Usuario: admin, Contraseña: admin123
    }
    return admin_credenciales.get(usuario) == contraseña

# Función para cerrar sesión de administrador
def cerrar_sesion_admin():
    st.session_state.admin_autenticado = False

# Pestaña 4: Administración
with tabs[3]:
    st.subheader("Área de Administración")
    st.markdown("Acceso restringido solo para administradores.")
    
    # Formulario de login si no está autenticado
    if not st.session_state.admin_autenticado:
        with st.form("login_admin"):
            st.write("Introduzca sus credenciales de administrador:")
            
            admin_usuario = st.text_input("Usuario", placeholder="Nombre de usuario")
            admin_contraseña = st.text_input("Contraseña", type="password", placeholder="Contraseña")
            
            login_button = st.form_submit_button("Iniciar Sesión")
            
            if login_button:
                if verificar_admin(admin_usuario, admin_contraseña):
                    st.success("Autenticación exitosa. Accediendo al panel de administración...")
                    st.session_state.admin_autenticado = True
                    st.rerun()  # Recargar para mostrar el contenido de administración
                else:
                    st.error("Credenciales incorrectas. Acceso denegado.")
    else:
        # Panel de administración
        st.success("¡Bienvenido, administrador!")
        
        # Botón para cerrar sesión
        if st.button("Cerrar Sesión de Administrador"):
            cerrar_sesion_admin()
            st.rerun()
        
        # Mostrar listado completo de autónomos registrados
        st.subheader(f"Listado Completo de Autónomos ({len(st.session_state.autonomos_registrados)})")
        
        if not st.session_state.autonomos_registrados:
            st.info("No hay autónomos registrados en el sistema.")
        else:
            # Crear un DataFrame con todos los autónomos para visualización
            datos_autonomos = []
            
            for autonomo in st.session_state.autonomos_registrados:
                datos_autonomos.append({
                    "ID": autonomo["ID"],
                    "Nombre": autonomo["Nombre completo"],
                    "DNI/NIE": autonomo["DNI/NIE"],
                    "Categoría": autonomo["Categoría"],
                    "Provincia": autonomo["Provincia"],
                    "Email": autonomo["Email"],
                    "Teléfono": autonomo["Teléfono"],
                    "Días disponibles": autonomo["Días disponibles"],
                    "Horario": autonomo["Horario"]
                })
            
            # Crear el DataFrame para la tabla
            df_admin = pd.DataFrame(datos_autonomos)
            
            # Mostrar la tabla con todos los autónomos
            st.dataframe(df_admin, use_container_width=True, height=400)
# Añadir un poco de estilo con CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
        border-bottom: 2px solid #4e8cff;
    }
    .stMarkdown {
        color: #495057;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
    }
    .admin-panel {
        background-color: #f1f8ff;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #cce5ff;
    }
</style>
""", unsafe_allow_html=True)