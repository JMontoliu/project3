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
    create_tables_if_not_exist(conn)
    return conn

def create_tables_if_not_exist(conn):
    try:
        cursor = conn.cursor()

        create_customers_query = """
    CREATE TABLE IF NOT EXISTS customers (
    id_persona VARCHAR(255) NOT NULL,
    id_autonomo VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(255) NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    status VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id_persona)
    );
        """
        cursor.execute(create_customers_query)

        create_clients_query = """
    CREATE TABLE IF NOT EXISTS clients (
    id_persona VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id_persona)
    );
        """
        cursor.execute(create_clients_query)
        
        conn.commit()
        cursor.close()
        logging.info("Tables created (if they didn't exist).")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        raise

def register_client(conn, data):
    try:
        cursor = conn.cursor()
        
        # Verificar si el cliente ya existe
        check_query = """
        SELECT COUNT(*) FROM clients
        WHERE id_persona = %s
        """
        cursor.execute(check_query, (data["id_persona"],))
        exists = cursor.fetchone()[0] > 0
        
        if not exists:

            insert_query = """
            INSERT INTO clients (id_persona, nombre, telefono, created_at)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data["id_persona"],
                data["nombre"],
                data["telefono"],
                data["created_at"]
            ))
            logging.info(f"Nuevo cliente registrado: {data['id_persona']}")
        
        cursor.close()
    except Exception as e:
        logging.error(f"Error registering client: {e}")
        raise


def insert_postgres(data):
    try:
        conn = get_postgres_connection()
        
        register_client(conn, data)
        
        cursor = conn.cursor()

        if data["status"] == "registrado":
            check_query = """
            SELECT COUNT(*) FROM customers 
            WHERE id_autonomo = %s 
            AND fecha_reserva = %s 
            AND hora_reserva = %s 
            AND status != 'cancelado'
            """
            cursor.execute(check_query, (
                data["id_autonomo"],
                data["fecha_reserva"],
                data["hora_reserva"]
            ))
            count = cursor.fetchone()[0]
            
            # Si ya existe una reserva en esa fecha y hora, salir sin insertar
            if count > 0:
                logging.info(f"Ya existe una reserva para el autónomo {data['id_autonomo']} en la fecha {data['fecha_reserva']} a las {data['hora_reserva']}. No se insertará.")
                conn.close()
                return
            

        insert_query = """
        INSERT INTO customers (id_persona, id_autonomo, nombre, telefono, fecha_reserva, hora_reserva, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_persona) DO UPDATE SET
            id_autonomo = EXCLUDED.id_autonomo,
            nombre = EXCLUDED.nombre,
            telefono = EXCLUDED.telefono,
            fecha_reserva = EXCLUDED.fecha_reserva,
            hora_reserva = EXCLUDED.hora_reserva,
            status = EXCLUDED.status,
            created_at = EXCLUDED.created_at
        """

        cursor.execute(insert_query, (
            data["id_persona"],
            data["id_autonomo"],
            data["nombre"],
            data["telefono"],
            data["fecha_reserva"],
            data["hora_reserva"],
            data["status"],
            data["created_at"]
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data inserted into PostgreSQL.")
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