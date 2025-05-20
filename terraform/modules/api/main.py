from fastapi import FastAPI, HTTPException, Body
from google.cloud import pubsub_v1
import psycopg2
import os
import json

app = FastAPI()

# Configuración Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "chatbot-topic")
PROJECT_ID  = os.getenv("PROJECT_ID", "dataproject03")
publisher   = pubsub_v1.PublisherClient()
topic_path  = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

# Helper para la conexión a Cloud SQL
def get_conn():
    return psycopg2.connect(
        host     = os.getenv("DB_HOST"),
        database = os.getenv("DB_NAME"),
        user     = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        port     = os.getenv("DB_PORT")
    )

@app.post("/publish")
def publish_message(payload: dict = Body(...)):
    """
    Publica directamente el JSON recibido en Pub/Sub.
    No necesita envolver el objeto en "data".
    """
    try:
        msg_json = json.dumps(payload)
        future   = publisher.publish(topic_path, msg_json.encode("utf-8"))
        return {"message_id": future.result()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Pub/Sub: {e}")

@app.get("/read/customers")
def read_customers():
    """
    Lee todos los registros de la tabla customers.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id_persona, id_autonomo, nombre, telefono,
                   fecha_reserva, hora_reserva, status, created_at
            FROM customers
        """)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer customers: {e}")

@app.get("/read/clients")
def read_clients():
    """
    Lee todos los registros de la tabla clients.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id_persona, nombre, telefono, created_at
            FROM clients
        """)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer clients: {e}")
