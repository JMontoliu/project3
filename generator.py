import uuid
import random
import time
import json
from faker import Faker
from datetime import datetime
from google.cloud import pubsub_v1

# CONFIGURA ESTOS VALORES
PROJECT_ID = "dataproject03"
TOPIC_ID = "pruebatopic"

fake = Faker('es_ES')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def generar_reserva():
    id_persona = str(uuid.uuid4())
    nombre = fake.name()
    telefono = fake.phone_number()
    fecha_reserva = fake.date_between(start_date="today", end_date="+30d").strftime("%Y-%m-%d")
    hora_reserva = fake.time(pattern="%H:%M:%S")
    status = random.choice(["pendiente", "confirmada", "cancelada", "realizada"])
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id_persona": id_persona,
        "nombre": nombre,
        "telefono": telefono,
        "fecha_reserva": fecha_reserva,
        "hora_reserva": hora_reserva,
        "status": status,
        "created_at": created_at
    }

# Enviar 10 reservas con delay
for _ in range(10):
    reserva = generar_reserva()
    data_json = json.dumps(reserva).encode("utf-8")
    future = publisher.publish(topic_path, data=data_json)
    print(f"Mensaje enviado: {reserva}")
    time.sleep(5)
