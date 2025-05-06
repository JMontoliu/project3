from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1
from google.cloud import firestore
from typing import List
import os
import json

app = FastAPI(
    title="Customer API",
    description="API para publicar en Pub/Sub y leer de Firestore",
    version="1.0.0"
)

# Configuración Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "customers")
PROJECT_ID = os.getenv("PROJECT_ID", "tu-project-id")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

# Configuración Firestore
db = firestore.Client()

# Modelos
class PublishRequest(BaseModel):
    data: dict

class CustomerItem(BaseModel):
    id: str
    data: dict

@app.get("/")
def root():
    return {"status": "API funcionando correctamente"}

@app.post("/publish")
def publish_message(req: PublishRequest):
    try:
        # Convertir el dict a JSON string para enviar a Pub/Sub
        message_json = json.dumps(req.data)
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        message_id = future.result()
        return {"message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar a Pub/Sub: {e}")

@app.get("/read", response_model=List[CustomerItem])
def read_customers():
    try:
        customers_ref = db.collection("customers")
        docs = customers_ref.stream()

        customers = []
        for doc in docs:
            customers.append(CustomerItem(id=doc.id, data=doc.to_dict()))
        
        return customers

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Firestore: {e}")
