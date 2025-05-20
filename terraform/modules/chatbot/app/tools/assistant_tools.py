from langchain_core.tools import tool
import requests
from datetime import datetime
import random
import pytz # Para zonas horarias
import os   # Para acceder a variables de entorno
import json # Para manejar JSON

relative_path_products = "app/data/products.txt" 

@tool
def get_current_datetime_in_spain() -> str:
    """
    Devuelve la fecha y hora actual exacta en España (zona horaria de Madrid/Península).
    Esencial para contextualizar conversaciones, verificar si una fecha propuesta es en el pasado,
    o para cualquier planificación que dependa del momento presente.
    No requiere argumentos.
    Ejemplo de salida: 'La fecha y hora actual en España es: Sábado, 18 de mayo de 2024, 15:30:00 CEST+0200'.
    """
    try:
        timezone_spain = pytz.timezone('Europe/Madrid')
        now_in_spain = datetime.now(timezone_spain)
        return f"La fecha y hora actual en España es: {now_in_spain.strftime('%A, %d de %B de %Y, %H:%M:%S %Z%z')}."
    except Exception as e:
        print(f"Error en get_current_datetime_in_spain: {e}")
        return "Lo siento, no pude obtener la fecha y hora actual en este momento."


@tool
def registrar_cita(
    nombre: str,
    telefono: str,
    producto: str, # Asegúrate que el LLM pasa esto con 'p' minúscula
    precio: int,   # Asegúrate que el LLM pasa esto con 'P' minúscula o como lo tengas en el docstring
    fecha_reserva: str,
    hora_reserva: str
) -> str:
    """ 
    Registra una NUEVA cita en el sistema para un cliente. Esta acción guarda la reserva.
    Se DEBEN proporcionar TODOS los siguientes datos como argumentos:
    - nombre (str): Nombre completo del cliente.
    - telefono (str): Número de teléfono de contacto del cliente.
    - producto (str): El nombre del producto o servicio que se va a reservar (ej. 'Pack Newborn', 'Pack Embarazo', 'Pack New Born').
    - precio (int): El precio del producto o servicio que se va a reservar (ej. 150, 200, 250). Se obtiene con la información de los productos.
    - fecha_reserva (str): Fecha deseada para la cita en formato YYYY-MM-DD.
    - hora_reserva (str): Hora deseada para la cita en formato HH:MM (24h).
    """
    print("--- Tool: registrar_cita ---")
    print(f"DEBUG: Argumentos recibidos -> Nombre: {nombre}, Teléfono: {telefono}, Producto: {producto}, Precio: {precio}, Fecha: {fecha_reserva}, Hora: {hora_reserva}")

    hora_reserva_api = f"{hora_reserva}:00" if len(hora_reserva) == 5 and ":" in hora_reserva else hora_reserva
    print(f"DEBUG: Hora formateada para API: {hora_reserva_api}")
    
    url_from_env = os.getenv("CUSTOMER_API_URL")
    print(f"DEBUG: CUSTOMER_API_URL leída del entorno: '{url_from_env}'")

    if not url_from_env:
        error_msg = "Error Crítico: La variable de entorno CUSTOMER_API_URL no está configurada."
        print(f"DEBUG: {error_msg}")
        return error_msg
        
    url = url_from_env.rstrip("/")
    if not url.endswith("/publish"): # Solo añadir /publish si la URL base no lo tiene
        url += "/publish"
    print(f"DEBUG: URL final para la API: '{url}'")

    # Payload ajustado para parecerse más al de Postman
    payload = {
        "id_persona": str(random.randint(10000, 99999)),
        "id_autonomo": "sara1234", # Asumiendo que este es fijo para Sarashot
        "nombre": nombre,
        "telefono": telefono,
        "producto": producto, # Usar el argumento como se recibe
        "precio": precio,     # Usar el argumento como se recibe
        "fecha_reserva": fecha_reserva,
        "hora_reserva": hora_reserva_api,
        "status": "registrado",
        "created_at": datetime.now(pytz.utc).isoformat().replace("+00:00", "Z"), # Formato ISO 8601 UTC
    }
    print(f"DEBUG: Payload a enviar (JSON): {json.dumps(payload, indent=2)}")

    try:
        print(f"DEBUG: Intentando POST a {url}...")
        response = requests.post(url, json=payload, timeout=20) # Aumentado el timeout a 20s
        
        print(f"DEBUG: Respuesta recibida. Status Code: {response.status_code}")
        try:
            # Intentar imprimir el cuerpo de la respuesta como texto, incluso si no es JSON
            response_text = response.text
            print(f"DEBUG: Cuerpo de la respuesta (texto): {response_text}")
        except Exception as text_ex:
            print(f"DEBUG: No se pudo obtener el cuerpo de la respuesta como texto: {text_ex}")
            response_text = "[Cuerpo de respuesta no legible]"

        # El API devuelve 202 Accepted en tu prueba de Postman
        if response.status_code == 202:
            try:
                response_json = response.json()
                if response_json.get("status") == "accepted":
                    success_msg = f"Cita para {nombre} enviada y aceptada por el sistema."
                    print(f"DEBUG: {success_msg}")
                    return success_msg
                else:
                    warn_msg = f"Cita para {nombre} enviada (status 202), pero estado de respuesta API inesperado: {response_json.get('status')}"
                    print(f"DEBUG: {warn_msg}")
                    return warn_msg
            except ValueError: # Si el cuerpo de la respuesta 202 no es JSON
                info_msg = f"Cita para {nombre} enviada (status 202), pero la respuesta de la API no fue JSON. Respuesta texto: {response_text}"
                print(f"DEBUG: {info_msg}")
                return info_msg
        elif response.status_code == 200: # Manejar 200 OK también como éxito
            success_msg_200 = f"Cita registrada para {nombre} con éxito (Status 200)."
            print(f"DEBUG: {success_msg_200}")
            return success_msg_200
        else:
            # Intentar obtener un mensaje de error más detallado del JSON si es posible
            error_detail = response_text # Usar el texto como fallback
            try:
                error_json = response.json()
                # Para errores de validación de FastAPI/Pydantic
                if "detail" in error_json: 
                    if isinstance(error_json["detail"], list) and error_json["detail"]:
                        first_error = error_json["detail"][0]
                        error_msg_val = first_error.get("msg", "Error de validación")
                        error_loc_val = str(first_error.get("loc", ""))
                        error_detail = f"Validación fallida: {error_msg_val} en campo(s) {error_loc_val}."
                    elif isinstance(error_json["detail"], str):
                        error_detail = error_json["detail"]
                elif isinstance(error_json, dict) and not error_detail: 
                    error_detail = str(error_json)
            except ValueError: # La respuesta de error no era JSON
                pass 
            
            final_error_msg = f"Error al registrar cita. Status HTTP: {response.status_code}. Detalle API: {error_detail}"
            print(f"DEBUG: {final_error_msg}")
            return final_error_msg
            
    except requests.exceptions.Timeout:
        timeout_msg = f"Error de conexión: Timeout (20s) esperando respuesta de {url}"
        print(f"DEBUG: {timeout_msg}")
        return timeout_msg
    except requests.exceptions.ConnectionError:
        conn_error_msg = f"Error de conexión: No se pudo conectar a {url}. ¿Está el servicio API corriendo y accesible desde este contenedor/entorno?"
        print(f"DEBUG: {conn_error_msg}")
        return conn_error_msg
    except requests.exceptions.RequestException as req_ex: # Otros errores de la librería requests
        req_error_msg = f"Error en la petición HTTP: {str(req_ex)}"
        print(f"DEBUG: {req_error_msg}")
        return req_error_msg
    except Exception as e: # Captura cualquier otro error inesperado
        import traceback
        unexpected_error_msg = f"Error inesperado en la herramienta registrar_cita: {str(e)}"
        print(f"DEBUG: {unexpected_error_msg}")
        print(f"DEBUG: Traceback completo del error inesperado:\n{traceback.format_exc()}")
        return unexpected_error_msg
    

@tool
def modificar_reserva(
    nombre: str,
    telefono: str,
    nueva_fecha: str,
    nueva_hora: str
) -> str:
    """
    Modifica los detalles de una cita YA EXISTENTE en el sistema para un cliente.
    Se necesita identificar la cita original (usando nombre y teléfono del cliente) y los nuevos detalles.
    Argumentos requeridos:
    - nombre (str): Nombre completo del cliente de la cita original.
    - telefono (str): Número de teléfono del cliente de la cita original.
    - nueva_fecha (str): Nueva fecha deseada para la cita en formato YYYY-MM-DD.
    - nueva_hora (str): Nueva hora deseada para la cita en formato HH:MM (24h).
    Devuelve un mensaje de confirmación del cambio o un error si no se pudo modificar.
    """
    url = os.getenv("CUSTOMER_API_URL").rstrip("/")
    if not url:
        return "Error: CUSTOMER_API_URL no está configurada."
    if not url.endswith("/publish"):
        url += "/publish"

    nueva_hora_api = f"{nueva_hora}:00" if len(nueva_hora) == 5 else nueva_hora
    
    data_cancel = {
        "id_persona": random.randint(1, 99999),  # Número aleatorio como ID
        "id_autonomo": "sara1234",
        "nombre": nombre,
        "telefono": telefono,
        "fecha_reserva": None,
        "hora_reserva": None,
        "status": "cancelado",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    new_data = {
        "id_persona": random.randint(1, 99999),  # Número aleatorio como ID
        "id_autonomo": "sara1234",
        "nombre": nombre,
        "telefono": telefono,
        "fecha_reserva": nueva_fecha,
        "hora_reserva": nueva_hora_api,
        "status": "registrado",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        cancel_response = requests.post(url, json=data_cancel)
        if cancel_response.status_code != 200:
            return f"Error al cancelar cita: {cancel_response.text}"

        new_response = requests.post(url, json=new_data)
        if new_response.status_code == 200:
            return f"Nueva cita registrada para {nombre} con éxito."
        else:
            return f"Error al registrar nueva cita: {new_response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"



@tool
def cancelar_reserva(
    nombre: str,
    telefono: str
) -> str:
    """
    Cancela una cita YA EXISTENTE en el sistema para un cliente.
    Se necesita identificar la cita a cancelar usando el nombre y teléfono del cliente.
    Argumentos requeridos:
    - nombre (str): Nombre completo del cliente de la cita a cancelar.
    - telefono (str): Número de teléfono del cliente de la cita a cancelar.
    Devuelve un mensaje de confirmación de la cancelación o un error si no se pudo cancelar.
    """
    
    url = os.getenv("CUSTOMER_API_URL").rstrip("/")
    if not url:
        return "Error: CUSTOMER_API_URL no está configurada."
    if not url.endswith("/publish"):
        url += "/publish"

    data = {
        "id_persona": random.randint(1, 99999),  # Número aleatorio como ID
        "id_autonomo": "sara1234",
        "nombre": nombre,
        "telefono": telefono,
        "fecha_reserva": None,
        "hora_reserva": None,
        "status": "cancelado",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return f"Cita cancelada para {nombre} con éxito."
        else:
            return f"Error al cancelar cita: {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

@tool
def get_weather_forecast_simple(location: str = "Valencia,Spain") -> str:
    """
    Consulta el pronóstico del tiempo actual y para los próximos 1-2 días para una ubicación específica.
    Es muy útil para planificar sesiones fotográficas en exterior.
    Si el usuario no especifica una ubicación, por defecto se usará 'Valencia,Spain'.
    Argumentos:
    - location (str, opcional): La ubicación para el pronóstico. Puede ser 'Ciudad', 'Ciudad,CodigoPais' (ej. 'Madrid,ES'), 'lat,lon', o código postal. Por defecto es 'Valencia,Spain'.
    Devuelve un informe del tiempo. Si el pronóstico incluye lluvia o condiciones adversas, menciónalo.    """
    api_key = os.getenv("WEATHERAPI_API_KEY")
    if not api_key:
        return "Error: La API key para el servicio de WeatherAPI no está configurada."

    # API endpoint para pronóstico (incluye el actual y hasta 3 días en el plan gratuito)
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    
    # Parámetros: key, q (ubicación), days (1 para solo actual + hoy, 2 o 3 para más días), lang (idioma)
    params = {
        "key": api_key,
        "q": location,
        "days": 2, # Actual + Mañana (puedes poner 1 si solo quieres el actual)
        "aqi": "no", # No necesitamos calidad del aire
        "alerts": "no", # No necesitamos alertas
        "lang": "es"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Información actual
        current_condition = data["current"]["condition"]["text"]
        current_temp = data["current"]["temp_c"]
        current_feels_like = data["current"]["feelslike_c"]
        
        report = f"Tiempo actual en {data['location']['name']}, {data['location']['country']}:\n"
        report += f"- Condición: {current_condition.capitalize()}\n"
        report += f"- Temperatura: {current_temp}°C (sensación: {current_feels_like}°C)\n"

        # Pronóstico para hoy y mañana (si se pidieron 'days: 2')
        if "forecast" in data and data["forecast"]["forecastday"]:
            for i, day_forecast in enumerate(data["forecast"]["forecastday"]):
                date_str = day_forecast["date"]
                day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A") # Obtener nombre del día
                if i == 0: # Hoy
                    day_label = f"Pronóstico para hoy ({day_name} {date_str})"
                else: # Mañana
                    day_label = f"Pronóstico para mañana ({day_name} {date_str})"
                
                day_data = day_forecast["day"]
                day_condition = day_data["condition"]["text"]
                max_temp = day_data["maxtemp_c"]
                min_temp = day_data["mintemp_c"]
                chance_of_rain = day_data.get("daily_chance_of_rain", "N/A") # Puede no estar en todos los planes/respuestas

                report += f"\n{day_label}:\n"
                report += f"- Condición: {day_condition.capitalize()}\n"
                report += f"- Max Temp: {max_temp}°C, Min Temp: {min_temp}°C\n"
                report += f"- Probabilidad de lluvia: {chance_of_rain}%\n"
        
        return report

    except requests.exceptions.HTTPError as http_err:
        error_data = http_err.response.json() if http_err.response else None
        error_message = error_data.get("error", {}).get("message", str(http_err)) if error_data else str(http_err)
        print(f"Error HTTP en WeatherAPI para {location}: {error_message}")
        return f"No se pudo obtener el tiempo para {location}. Razón: {error_message}"
    except requests.exceptions.RequestException as req_err:
        print(f"Error de red en WeatherAPI para {location}: {req_err}")
        return f"No se pudo conectar al servicio de meteorología para {location}."
    except Exception as e:
        print(f"Error inesperado en WeatherAPI para {location}: {e}")
        return f"Lo siento, ocurrió un error inesperado al obtener el tiempo para {location}."
    
@tool
def get_all_product_info_text() -> str:
    """
    Recupera la descripción COMPLETA de TODOS los productos y servicios fotográficos ofrecidos por Sarashot.
    DEBE usarse cuando el usuario haga preguntas generales sobre qué servicios hay, qué tipos de sesiones se ofrecen,
    o si necesita una visión global antes de preguntar por un servicio específico.
    Esta herramienta devuelve un ÚNICO string largo con toda la información. No requiere argumentos.
    El LLM que llama a esta herramienta es responsable de leer y extraer la información pertinente de este texto para responder al usuario.

    """
    print(f"Tool: get_all_product_info_text (ultra-simple) - Leyendo desde: {relative_path_products}")
    
    # Leer directamente el archivo. Si no existe o hay problemas, esto fallará con una excepción.
    with open(relative_path_products, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Tool: get_all_product_info_text - Contenido recuperado (primeros 300 chars):\n{content[:300]}...")
    return content
 

all_assistant_tools = [
    registrar_cita, 
    modificar_reserva, 
    cancelar_reserva, 
    get_current_datetime_in_spain,
    get_weather_forecast_simple,
    get_all_product_info_text
]

