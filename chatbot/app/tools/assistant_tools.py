from langchain_core.tools import tool
import requests
from datetime import datetime
import random
import pytz # Para zonas horarias
import os   # Para acceder a variables de entorno


@tool
def get_current_datetime_in_spain() -> str:
    """
    Devuelve la fecha y hora actual en España (Madrid/Península).
    Útil para saber el momento exacto de la conversación o para planificar respecto al ahora.
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
    Registra una cita con los siguientes datos:
    - nombre
    - telefono
    - fecha_reserva
    - hora_reserva
    (id_persona aleatorio, created_at actual, status=False)
    """
    url = "https://customer-api-196041114036.europe-west1.run.app/publish"

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
    Modifica una reserva existente.
    - nombre
    - telefono
    - nueva_fecha
    - nueva_hora
    """
    """Modifica una reserva existente con nueva_fecha y nueva_hora."""

    return f"Simulación: Reserva para {nombre} modificada a {nueva_fecha} {nueva_hora}."



@tool
def cancelar_reserva(
    nombre: str,
    telefono: str
) -> str:
    """
    Cancela una reserva existente.
    - nombre
    - telefono
    """
    return f"Simulación: Reserva para {nombre} cancelada."



@tool
def consultar_horarios_disponibles(
    fecha: str
) -> str:
    """
    Consulta los horarios disponibles para una fecha dada.
    - fecha
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
    Confirma una reserva pendiente.
    - nombre
    - telefono
    """
    return f"Simulación: Reserva para {nombre} confirmada."

@tool
def get_weather_forecast_simple(location: str = "Valencia,Spain") -> str:
    """
    Obtiene el pronóstico del tiempo actual y para los próximos 1-2 días para una ubicación.
    Por defecto, consulta el tiempo en Valencia, España.
    El formato de 'location' puede ser Ciudad, 'lat,lon', o código postal.
    """
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

all_assistant_tools = [
    registrar_cita, 
    modificar_reserva, 
    cancelar_reserva, 
    consultar_horarios_disponibles, 
    confirmar_reserva,
    get_current_datetime_in_spain,
    get_weather_forecast_simple
]

