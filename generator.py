import uuid
import random
import time
import json
from faker import Faker
from datetime import datetime
from google.cloud import pubsub_v1

PROJECT_ID = "dataproject03"
TOPIC_ID = "chatbot-topic"

fake = Faker("es_ES")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def generar_reserva():
    return {
        "id_persona": "id45",
        "id_autonomo": "peluqueria112",
        "nombre": "marcos",
        "telefono": fake.phone_number(),
        "fecha_reserva": "2023-10-11",
        "hora_reserva": "16:00:00",
        "status": random.choice(["cancelado"]),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


for _ in range(15):
    reserva = generar_reserva()
    data_json = json.dumps(reserva).encode("utf-8")
    publisher.publish(topic_path, data=data_json)
    print(f"Mensaje enviado: {reserva}")
    time.sleep(5)
