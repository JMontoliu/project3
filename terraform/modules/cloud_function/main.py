import base64
import functions_framework
from datetime import datetime
import os
import logging
import json
import psycopg2
from google.cloud import bigquery
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ID = os.getenv("PROJECT_ID", "dataproject03")
REGION = os.getenv("REGION", "europe-west1")
BQ_DATASET = os.getenv("BQ_DATASET", "chatbot_dataset")

PG_DATABASE = os.getenv("PG_DATABASE", "reservas_db")
PG_USER = os.getenv("PG_USER", "postgres_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_HOST = os.getenv("PG_HOST", "localhost")
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
            id_ticket VARCHAR(36) NOT NULL,
            id_persona VARCHAR(255) NOT NULL,
            id_autonomo VARCHAR(255) NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            telefono VARCHAR(255) NOT NULL,
            fecha_reserva DATE NOT NULL,
            hora_reserva TIME NOT NULL,
            status VARCHAR(255) NOT NULL,
            producto VARCHAR(255) NOT NULL,
            precio INT64 NOT NULL,
            created_at TIMESTAMP NOT NULL,
            PRIMARY KEY (id_ticket),
            UNIQUE (id_persona, id_autonomo, fecha_reserva, hora_reserva)
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
            
            if count > 0:
                logging.info(f"Ya existe una reserva para el autónomo {data['id_autonomo']} en la fecha {data['fecha_reserva']} a las {data['hora_reserva']}. No se insertará.")
                conn.close()
                return
        
        elif data["status"] == "cancelado":
            check_query = """
            SELECT id_ticket FROM customers 
            WHERE id_persona = %s
            AND id_autonomo = %s 
            AND fecha_reserva = %s 
            AND hora_reserva = %s 
            AND status != 'cancelado'
            """
            cursor.execute(check_query, (
                data["id_persona"],
                data["id_autonomo"],
                data["fecha_reserva"],
                data["hora_reserva"]
            ))
            
            result = cursor.fetchone()
            if result:
                id_ticket = result[0]
                update_query = """
                UPDATE customers 
                SET status = 'cancelado', created_at = %s
                WHERE id_ticket = %s
                """
                cursor.execute(update_query, (
                    data["created_at"],
                    id_ticket
                ))
                conn.commit()
                logging.info(f"Reserva cancelada para persona {data['id_persona']} con autónomo {data['id_autonomo']} en fecha {data['fecha_reserva']} a las {data['hora_reserva']}. Ticket: {id_ticket}")
                
                data["id_ticket"] = id_ticket
                
                cursor.close()
                conn.close()
                return
            else:
                logging.info(f"La persona {data['id_persona']} no tiene una reserva activa con el autónomo {data['id_autonomo']} en fecha {data['fecha_reserva']} a las {data['hora_reserva']}. No se procesará la cancelación.")
                conn.close()
                return

        id_ticket = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO customers (id_ticket, id_persona, id_autonomo, nombre, telefono, fecha_reserva, hora_reserva, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_persona, id_autonomo, fecha_reserva, hora_reserva) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            telefono = EXCLUDED.telefono,
            status = EXCLUDED.status,
            producto = EXCLUDED.producto,
            precio = EXCLUDED.precio,
            created_at = EXCLUDED.created_at
        """

        cursor.execute(insert_query, (
            id_ticket,
            data["id_persona"],
            data["id_autonomo"],
            data["nombre"],
            data["telefono"],
            data["fecha_reserva"],
            data["hora_reserva"],
            data["status"],
            data["producto"],
            data["precio"],
            data["created_at"]
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Data inserted into PostgreSQL with ticket ID: {id_ticket}")
        
        data["id_ticket"] = id_ticket
        
    except Exception as e:
        logging.error(f"Error inserting data PostgreSQL: {e}")
        raise

def insert_to_bigquery(data):
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        if "id_persona" in data and "nombre" in data and "telefono" in data:
            insert_client_to_bigquery(client, data)
        
        if "id_persona" in data and "id_autonomo" in data:
            insert_reservation_to_bigquery(client, data)
            
    except Exception as e:
        logging.error(f"Error al insertar en BigQuery: {e}")

def insert_client_to_bigquery(client, data):
    try:
        table_id = f"{PROJECT_ID}.{BQ_DATASET}.clients"
        
        query = f"""
        SELECT COUNT(*) as count
        FROM `{PROJECT_ID}.{BQ_DATASET}.clients`
        WHERE id_persona = '{data["id_persona"]}'
        """
        
        query_job = client.query(query)
        results = list(query_job)
        
        if results and results[0]['count'] > 0:
            logging.info(f"Cliente ya existe en BigQuery, no se insertará nuevamente: {data['id_persona']}")
            return
        
        rows_to_insert = [{
            "id_persona": data["id_persona"],
            "nombre": data["nombre"],
            "telefono": data["telefono"],
            "created_at": data["created_at"]
        }]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors == []:
            logging.info(f"Cliente insertado en BigQuery: {data['id_persona']}")
        else:
            logging.error(f"Errores al insertar en BigQuery (clients): {errors}")
    except Exception as e:
        logging.error(f"Error al insertar cliente en BigQuery: {e}")

def insert_reservation_to_bigquery(client, data):
    try:
        required_fields = ["id_persona", "id_autonomo", "nombre", "telefono", 
                           "fecha_reserva", "hora_reserva", "status", "producto", "precio", "created_at"]
        if not all(field in data for field in required_fields):
            logging.error("Faltan campos requeridos para insertar en la tabla de reservas")
            return
        
        table_id = f"{PROJECT_ID}.{BQ_DATASET}.reservas"
        
        hora_reserva = data["hora_reserva"]
        if ":" in hora_reserva and len(hora_reserva.split(":")) == 2:
            hora_reserva = f"{hora_reserva}:00"
        
        if "id_ticket" not in data:
            data["id_ticket"] = str(uuid.uuid4())
            logging.warning(f"Generando nuevo id_ticket para BigQuery: {data['id_ticket']}")
        
        if data["status"] == "cancelado":
            try:
                search_query = f"""
                SELECT COUNT(*) as count 
                FROM `{PROJECT_ID}.{BQ_DATASET}.reservas`
                WHERE id_ticket = '{data["id_ticket"]}'
                """
                
                query_job = client.query(search_query)
                results = list(query_job)
                
                if results and results[0]['count'] > 0:
                    update_query = f"""
                    UPDATE `{PROJECT_ID}.{BQ_DATASET}.reservas`
                    SET status = 'cancelado', created_at = '{data["created_at"]}'
                    WHERE id_ticket = '{data["id_ticket"]}'
                    """
                    
                    query_job = client.query(update_query)
                    query_job.result()
                    
                    logging.info(f"Reserva actualizada a 'cancelado' en BigQuery. Ticket: {data['id_ticket']}")
                    return
            except Exception as e:
                logging.error(f"Error al intentar actualizar reserva cancelada: {e}")
        
        row_data = {
            "id_ticket": data["id_ticket"],
            "id_persona": data["id_persona"],
            "id_autonomo": data["id_autonomo"],
            "nombre": data["nombre"],
            "telefono": data["telefono"],
            "fecha_reserva": data["fecha_reserva"],
            "hora_reserva": hora_reserva,
            "status": data["status"],
            "producto": data["producto"],
            "precio": data["precio"],
            "created_at": data["created_at"]
        }
        
        rows_to_insert = [row_data]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors == []:
            logging.info(f"Reserva insertada en BigQuery: {data['id_persona']} - {data['fecha_reserva']} {hora_reserva} - Status: {data['status']} - Ticket: {data['id_ticket']}")
        else:
            logging.error(f"Errores al insertar en BigQuery (reservas): {errors}")
    except Exception as e:
        logging.error(f"Error al insertar reserva en BigQuery: {e}")

@functions_framework.cloud_event
def process_pubsub_message(cloud_event):
    try:
        data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()
        
        insert_postgres(data)
        insert_to_bigquery(data)
        
        logging.info("Procesamiento completado con éxito")
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {e}")
        raise