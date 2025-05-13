from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1
from google.cloud import bigquery
import json
import os

app = FastAPI()

# Configuración Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "chatbot-topic")
PROJECT_ID = os.getenv("PROJECT_ID", "dataproject03")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

# Modelo para publicación
class PublishRequest(BaseModel):
    data: dict

@app.post("/publish")
def publish_message(req: PublishRequest):
    try:
        msg_json = json.dumps(req.data)
        future = publisher.publish(topic_path, msg_json.encode("utf-8"))
        return {"message_id": future.result()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Pub/Sub: {e}")

@app.get("/read")
def read_customers():
    try:
        client = bigquery.Client(location="US")
        query = """
            SELECT id_persona, nombre, telefono, fecha_reserva, hora_reserva, status, created_at
            FROM `dataproject03.chatbot_dataset.customers`
        """
        query_job = client.query(query)
        results = []
        for row in query_job:
            results.append({
                "id_persona": row["id_persona"],
                "nombre": row["nombre"],
                "telefono": row["telefono"],
                "fecha_reserva": str(row["fecha_reserva"]),
                "hora_reserva": str(row["hora_reserva"]),
                "status": row["status"],
                "created_at": str(row["created_at"])
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer BigQuery: {e}")
