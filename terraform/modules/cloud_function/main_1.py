import base64
import json
import os
import logging
import functions_framework
import psycopg2
from datetime import datetime
from google.cloud import bigquery

# Configuración de logging
debug_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, debug_level))
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
PROJECT_ID = os.environ.get('PROJECT_ID')
BQ_DATASET = os.environ.get('DATASET')
BQ_TABLE = os.environ.get('TABLES')

# Configuración para PostgreSQL
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT', '5432')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_DATABASE = os.environ.get('PG_DATABASE')

# Esquema para la tabla PostgreSQL
PG_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
  id_persona VARCHAR(255) NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  telefono VARCHAR(255) NOT NULL,
  fecha_reserva DATE NOT NULL,
  hora_reserva TIME NOT NULL,
  status VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id_persona)
);
"""

def get_pg_connection():
    """Establece conexión con PostgreSQL"""
    try:
        # Añade logs para depuración
        logger.info(f"PG_HOST desde variable de entorno: {os.environ.get('PG_HOST')}")
        logger.info(f"PG_HOST variable en Python: {PG_HOST}")
        
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DATABASE,
            connect_timeout=30
        )
        logger.info("Conexión a PostgreSQL establecida.")
        return conn
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        # Log completo de todas las variables usadas
        logger.error(f"Variables usadas: HOST={PG_HOST}, PORT={PG_PORT}, USER={PG_USER}, DB={PG_DATABASE}")
        raise

def ensure_pg_table_exists(conn):
    """Asegura que la tabla existe en PostgreSQL"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(PG_TABLE_SCHEMA)
            conn.commit()
            logger.info("Tabla PostgreSQL verificada/creada correctamente.")
    except Exception as e:
        logger.error(f"Error al crear la tabla en PostgreSQL: {e}")
        raise

def insert_into_pg(conn, data):
    """Inserta datos en PostgreSQL"""
    query = """
    INSERT INTO customers (id_persona, nombre, telefono, fecha_reserva, hora_reserva, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id_persona) DO UPDATE SET
        nombre = EXCLUDED.nombre,
        telefono = EXCLUDED.telefono,
        fecha_reserva = EXCLUDED.fecha_reserva,
        hora_reserva = EXCLUDED.hora_reserva,
        status = EXCLUDED.status,
        created_at = EXCLUDED.created_at
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (
                data['id_persona'],
                data['nombre'],
                data['telefono'],
                data['fecha_reserva'],
                data['hora_reserva'],
                data['status'],
                data['created_at']
            ))
            conn.commit()
            logger.info(f"Datos insertados en PostgreSQL para id_persona: {data['id_persona']}")
    except Exception as e:
        logger.error(f"Error al insertar en PostgreSQL: {e}")
        conn.rollback()
        raise

def insert_into_bigquery(data):
    """Inserta datos en BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
    rows_to_insert = [{
        'id_persona': data['id_persona'],
        'nombre': data['nombre'],
        'telefono': data['telefono'],
        'fecha_reserva': data['fecha_reserva'],
        'hora_reserva': data['hora_reserva'],
        'status': data['status'],
        'created_at': data['created_at']
    }]
    try:
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if not errors:
            logger.info(f"Datos insertados en BigQuery para id_persona: {data['id_persona']}")
        else:
            logger.error(f"Errores al insertar en BigQuery: {errors}")
            raise Exception(f"Error en BigQuery: {errors}")
    except Exception as e:
        logger.error(f"Error al insertar en BigQuery: {e}")
        raise

@functions_framework.cloud_event
def process_pubsub_message(cloud_event):
    """Función principal que se invoca desde PubSub en GCF v2"""
    # Log al activarse la función
    logger.info("Cloud Function invocada: process_pubsub_message ha iniciado el procesamiento.")
    try:
        if cloud_event.data and cloud_event.data.get('message'):
            message = cloud_event.data.get('message', {})
            if 'data' in message:
                pubsub_message = base64.b64decode(message['data']).decode('utf-8')
                data = json.loads(pubsub_message)
                logger.info(f"Mensaje recibido del Pub/Sub: {data}")
                required_fields = ['id_persona', 'nombre', 'telefono', 'fecha_reserva', 'hora_reserva', 'status']
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Campo requerido no encontrado: {field}")
                        return
                if 'created_at' not in data:
                    data['created_at'] = datetime.now().isoformat()
                conn = get_pg_connection()
                ensure_pg_table_exists(conn)
                insert_into_pg(conn, data)
                insert_into_bigquery(data)
                conn.close()
                logger.info("Procesamiento completado exitosamente.")
            else:
                logger.warning("No hay datos en el mensaje.")
        else:
            logger.warning("Evento no contiene datos válidos.")
    except Exception as e:
        logger.error(f"Error en el procesamiento: {e}")
        raise