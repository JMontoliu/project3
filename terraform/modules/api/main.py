from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1
import sqlalchemy
import json
import os

app = FastAPI()


PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "chatbot-topic")
PROJECT_ID = os.getenv("PROJECT_ID", "dataproject03")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)


DB_USER = os.getenv("admin")
DB_PASS = os.getenv("admin")
DB_NAME = os.getenv("db-chatbot")
DB_CONNECTION_NAME = os.getenv("DB_CONNECTION_NAME")

def get_db_engine():
    return sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            query={"unix_socket": f"/cloudsql/{DB_CONNECTION_NAME}"}
        )
    )


class PublishRequest(BaseModel):
    data: dict

class Customer(BaseModel):
    id: int
    name: str
    email: str


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
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT id, name, email FROM customers"))
            customers = [{"id": row.id, "name": row.name, "email": row.email} for row in result]
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en DB: {e}")
