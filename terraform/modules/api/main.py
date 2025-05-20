from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
from datetime import date, time, datetime
import json
import os
import psycopg2
from google.cloud import pubsub_v1


app = FastAPI()

class CustomerTicket(BaseModel):
    id_ticket: str
    id_persona: str
    id_autonomo: str
    nombre: str
    telefono: str
    fecha_reserva: date
    hora_reserva: time
    status: str
    created_at: datetime

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

@app.post("/publish", status_code=202)
def publish_message(payload: CustomerTicket = Body(...)):
    """
    Publica el JSON validado en Pub/Sub.
    """
    try:
        msg_json = payload.json()
        # Publicar sin bloquear:
        publisher.publish(topic_path, msg_json.encode("utf-8"))
        return {"status": "accepted"}
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

@app.get("/customers/count")
def count_customers(
    id_autonomo: int = Query(..., description="ID del autónomo"),
    fecha_reserva: str = Query(..., description="Fecha de la reserva (YYYY-MM-DD)"),
    hora_reserva: str = Query(..., description="Hora de la reserva (HH:MM:SS)")
):
    """
    Devuelve el número de registros en customers con status 'registrado'
    para el id_autonomo, fecha_reserva y hora_reserva proporcionados.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) 
            FROM customers 
            WHERE id_autonomo = %s 
              AND fecha_reserva = %s 
              AND hora_reserva = %s 
              AND status = 'registrado';
            """,
            (id_autonomo, fecha_reserva, hora_reserva)
        )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar customers: {e}")

@app.get("/customers/count/phone")
def count_customers_by_phone(
    telefono: str = Query(..., description="Teléfono del cliente")
):
    """
    Devuelve el número de registros en customers
    filtrados por el número de teléfono proporcionado.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) 
            FROM customers 
            WHERE telefono = %s;
            """,
            (telefono,)
        )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar por teléfono: {e}")
