import base64
import functions_framework
from datetime import datetime
import os
import logging
import json
import psycopg2


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ID  = os.getenv("PROJECT_ID", "default_project")
PG_DATABASE = os.getenv("PG_DATABASE", "default-db")
PG_USER = os.getenv("PG_USER", "user")
PG_PASSWORD =  os.getenv("PG_PASSWORD", "password")
PG_HOST = os.getenv("PG_HOST", "default_host")
PG_PORT = os.getenv("PG_PORT", "5432")

def get_postgres_connection():
    conn = psycopg2.connect(
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    create_table_if_not_exists(conn)
    return conn

def create_table_if_not_exists(conn):
    try:
        cursor = conn.cursor()
        create_table_query = """
    CREATE TABLE IF NOT EXISTS customers (
    id_reserva VARCHAR(255) NOT NULL,
    id_persona VARCHAR(255) NOT NULL,
    id_autonomo VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(255) NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    status VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id_reserva)
    );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        logging.info("Table customers created (if it didn't exist).")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        raise

def check_existing_booking(cursor, id_reserva):
    check_query = """
    SELECT COUNT(*) FROM customers 
    WHERE id_reserva = %s 
    AND status != 'cancelado'
    """
    cursor.execute(check_query, (id_reserva,))
    return cursor.fetchone()[0] > 0

def cancel_booking(cursor, data):
    update_query = """
    UPDATE customers 
    SET status = 'cancelado', created_at = %s
    WHERE id_reserva = %s
    """
    cursor.execute(update_query, (
        data["created_at"],
        data["id_reserva"]
    ))
    return cursor.rowcount > 0

def insert_or_update_booking(cursor, data):
    insert_query = """
    INSERT INTO customers (id_reserva, id_persona, id_autonomo, nombre, telefono, fecha_reserva, hora_reserva, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id_reserva) DO UPDATE SETD
        id_persona = EXCLUDED.id_persona,
        id_autonomo = EXCLUDED.id_autonomo,
        nombre = EXCLUDED.nombre,
        telefono = EXCLUDED.telefono,
        fecha_reserva = EXCLUDED.fecha_reserva,
        hora_reserva = EXCLUDED.hora_reserva,
        status = EXCLUDED.status,
        created_at = EXCLUDED.created_at
    """
    cursor.execute(insert_query, (
        data["id_reserva"],
        data["id_persona"],
        data["id_autonomo"],
        data["nombre"],
        data["telefono"],
        data["fecha_reserva"],
        data["hora_reserva"],
        data["status"],
        data["created_at"]
    ))

def insert_postgres(data):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        if data["status"] == "registrado":
            if check_existing_booking(cursor, data["id_reserva"]):
                logging.info(f"Ya existe una reserva activa con ID {data['id_reserva']}. No se insertará.")
                conn.close()
                return
        
        elif data["status"] == "cancelado":
            if cancel_booking(cursor, data):
                conn.commit()
                logging.info(f"Reserva {data['id_reserva']} cancelada.")
                cursor.close()
                conn.close()
                return
        
        insert_or_update_booking(cursor, data)

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Data inserted into PostgreSQL. Status: {data['status']}")
    except Exception as e:
        logging.error(f"Error inserting data PostgreSQL: {e}")
        raise

@functions_framework.cloud_event
def process_pubsub_message(cloud_event):
    try:
        data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()
        
        insert_postgres(data)
    except Exception as e:
        logging.error(f"Error trying to process register: {e}")
        raise