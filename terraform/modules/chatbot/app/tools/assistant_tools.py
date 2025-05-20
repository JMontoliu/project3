from langchain_core.tools import tool
import requests
from datetime import datetime
import random
import pytz # Para zonas horarias
import os   # Para acceder a variables de entorno

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
    fecha_reserva: str,
    hora_reserva: str
) -> str:
    """
    Registra una NUEVA cita en el sistema para un cliente. Esta acción guarda la reserva.
    Se DEBEN proporcionar TODOS los siguientes datos como argumentos:
    - nombre (str): Nombre completo del cliente.
    - telefono (str): Número de teléfono de contacto del cliente.
    - fecha_reserva (str): Fecha deseada para la cita en formato YYYY-MM-DD.
    - hora_reserva (str): Hora deseada para la cita en formato HH:MM (24h).
    - tipo_sesion (str): El tipo específico de sesión fotográfica que se va a reservar (ej. 'Sesión Newborn Clásica', 'Sesión Embarazo Exterior', 'Pack Dulce Espera').
    Devuelve un mensaje de confirmación con un ID de cita si tiene éxito, o un mensaje de error si el registro falla.
    """
    url = os.getenv("CUSTOMER_API_URL", "").rstrip("/")
    if not url:
        return "Error: CUSTOMER_API_URL no está configurada."
    if not url.endswith("/publish"):
        url += "/publish"

    payload = {
        "data": {
            "user_id": random.randint(1, 99999),  # Número aleatorio como ID
            "nombre": nombre,
            "telefono": telefono,
            "fecha_reserva": fecha_reserva,
            "hora_reserva": hora_reserva,
            "status": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return f"Cita registrada para {nombre} con éxito."
        else:
            return f"Error al registrar cita: {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"
    

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

    return f"Simulación: Reserva para {nombre} modificada a {nueva_fecha} {nueva_hora}."



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
    return f"Simulación: Reserva para {nombre} cancelada."



@tool
def consultar_horarios_disponibles(
    fecha: str
) -> str:
    """
    Consulta y devuelve los horarios de citas que están libres para una fecha específica.
    Útil cuando un cliente pregunta '¿qué horas tienes libres el día X?' o '¿hay hueco para el YYYY-MM-DD?'.
    Argumentos requeridos:
    - fecha (str): La fecha para la cual se quiere consultar la disponibilidad, en formato YYYY-MM-DD.
    Devuelve una lista de horarios disponibles para esa fecha o un mensaje indicando si no hay disponibilidad.
    """
    if "hoy" in fecha.lower() or datetime.now().strftime("%Y-%m-%d") in fecha:
        return "Simulación: Para hoy, disponibles a las 15:00, 16:00."
    return f"Simulación: Para {fecha}, disponibles a las 10:00, 11:00, 14:00."




@tool
def confirmar_reserva(
    nombre: str,
    telefono: str
) -> str:
    """
    Consulta y devuelve los horarios de citas que están libres para una fecha específica.
    Útil cuando un cliente pregunta '¿qué horas tienes libres el día X?' o '¿hay hueco para el YYYY-MM-DD?'.
    Argumentos requeridos:
    - fecha (str): La fecha para la cual se quiere consultar la disponibilidad, en formato YYYY-MM-DD.
    Devuelve una lista de horarios disponibles para esa fecha o un mensaje indicando si no hay disponibilidad.
    """
    return f"Simulación: Reserva para {nombre} confirmada."

@tool
def get_weather_forecast_simple(location: str = "Valencia,Spain") -> str:
    """
tiene el pronóstico del tiempo actual y para los próximos 1-2 días para una ubicación específica.
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
    consultar_horarios_disponibles, 
    confirmar_reserva,
    get_current_datetime_in_spain,
    get_weather_forecast_simple,
    get_all_product_info_text
]

