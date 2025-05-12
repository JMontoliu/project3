import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def process_pubsub_message(event, context):
    """Simple Cloud Function triggered by Pub/Sub.
    Args:
         event (dict): Event containing Pub/Sub data
         context: Metadata
    """
    # Get Pub/Sub message
    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        logging.info(f"Hello World! Received message: {pubsub_message}")
    else:
        logging.info("Hello World! Received an event without data")
    
    # Just return a success message
    return "OK", 200