import json
from decouple import config
import functions_framework
from google.cloud import pubsub_v1

# Initialise variables for Strava API
STRAVA_VERIFY_TOKEN = config('STRAVA_API__VERIFY_TOKEN')
STRAVA_CLIENT_SECRET = config('STRAVA_API__CLIENT_SECRET')
STRAVA_SUBSCRIPTION_ID = config('STRAVA_API__SUBSCRIPTION_ID')

# Initialise the Pub/Sub client
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = "strava-exploration-v2"
TOPIC_NAME = "strava-webhook-events"
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

@functions_framework.http
def strava_webhook_handler(request):
    """
    HTTP Cloud Function that handles Strava webhook events.
    Args:
        request (flask.Request): The request object.
    """
    print(f"Received request method: {request.method}")
    
    # --- Strava Webhook Subscription Validation (GET request) ---
    if request.method == 'GET':
        # Extract query parameters from the request
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Validate the request using the mode and token
        # If mode is 'subscribe' and token matches the verify token, return the challenge
        if mode == 'subscribe' and token == STRAVA_VERIFY_TOKEN:
            print(f"Webhook subscription verified! Challenge: {challenge}")
            return json.dumps({'hub.challenge': challenge}), 200, {'Content-Type': 'application/json'}
        # If verification fails, return a 403 error
        else:
            print(f"Webhook verification failed. Mode: {mode}, Token: {token}")
            return json.dumps({'error': 'Verification failed'}), 403, {'Content-Type': 'application/json'}

    # --- Strava Webhook Event Processing (POST request) ---
    elif request.method == 'POST':
        try:
            # Extract the JSON body from the request
            payload_bytes = request.get_data()

            # If the request payload is empty, return a 400 error
            if not payload_bytes:
                print("No body in POST request.")
                return json.dumps({'error': 'No body in request'}), 400, {'Content-Type': 'application/json'}

            # Parse the JSON body
            payload = json.loads(payload_bytes.decode('utf-8'))
            print(f"Received Strava webhook payload: {json.dumps(payload)}")

            # Verify the autheticity of the request using the subscription ID
            subscription_id = payload.get('subscription_id')
            print(f"Received subscription ID: {subscription_id}")
            # If subscription_id is not present or does not match the expected value, return a 401 error
            if not subscription_id or (subscription_id != int(STRAVA_SUBSCRIPTION_ID)):
                print("Invalid or missing subscription ID.")
                return json.dumps({'error': 'Invalid or missing subscription ID'}), 401, {'Content-Type': 'application/json'}
            
            # Extract the payload parameters
            object_type = payload.get('object_type')
            aspect_type = payload.get('aspect_type')
            object_id = payload.get('object_id')
            owner_id = payload.get('owner_id')

            # Process the webhook event based on the object type and aspect type
            if object_type == 'activity' and aspect_type == 'create':
                print(f"New activity created! Activity ID: {object_id}, Owner ID: {owner_id}")

                # Publish the event to the Pub/Sub topic
                future = publisher.publish(TOPIC_PATH, data=payload_bytes)
                # Wait for the publish operation to complete
                message_id = future.result()
                print(f"Published message with ID: {message_id} to topic: {TOPIC_PATH}")

            elif object_type == 'activity' and aspect_type == 'update':
                print(f"Activity updated! Activity ID: {object_id}, Owner ID: {owner_id}, Updates: {payload.get('updates')}")

                # Publish the event to the Pub/Sub topic
                future = publisher.publish(TOPIC_PATH, data=payload_bytes)
                # Wait for the publish operation to complete
                message_id = future.result()
                print(f"Published message with ID: {message_id} to topic: {TOPIC_PATH}")

            elif object_type == 'athlete' and aspect_type == 'update':
                print(f"Athlete updated! Athlete ID: {object_id}, Updates: {payload.get('updates')}")

            else:
                print(f"Unhandled event type: Object Type={object_type}, Aspect Type={aspect_type}")
                
            return json.dumps({'message': 'Webhook processed successfully'}), 200, {'Content-Type': 'application/json'}

        # Handle JSON parsing errors and other exceptions
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e} - Body: {request.get_data().decode('utf-8')}")
            return json.dumps({'error': 'Invalid JSON payload'}), 400, {'Content-Type': 'application/json'}
        except Exception as e:
            print(f"Unexpected error during POST request: {e}")
            return json.dumps({'error': 'Internal server error'}), 500, {'Content-Type': 'application/json'}
    
    # Handle unsupported HTTP methods
    else:
        print(f"Unsupported HTTP method: {request.method}")
        return json.dumps({'error': 'Method Not Allowed'}), 405, {'Content-Type': 'application/json'}