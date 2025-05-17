from langchain_core.tools import tool
import requests
from datetime import datetime
import random


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