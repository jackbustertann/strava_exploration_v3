import json
import hmac
import hashlib
from decouple import config
import functions_framework

STRAVA_VERIFY_TOKEN = config('STRAVA_API__VERIFY_TOKEN')
STRAVA_CLIENT_SECRET = config('STRAVA_API__CLIENT_SECRET')
STRAVA_SUBSCRIPTION_ID = config('STRAVA_API__SUBSCRIPTION_ID')

def verify_strava_signature(body_bytes, signature, secret_bytes):
    """
    Verifies the Strava webhook signature.

    Args:
        body_bytes (bytes): The raw, unparsed HTTP request body received from Strava, as bytes.
                            This is the content that Strava signed.
        signature (str): The value of the 'X-Hub-Signature' header from the incoming request.
                         It's expected to be in the format 'sha1=HEX_DIGEST'.
        secret_bytes (bytes): Your Strava Webhook Secret token, provided by Strava
                              when you set up your webhook, in byte format.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        # Strava's signature is 'sha1=' + HMAC-SHA1 of the request body using the webhook secret
        expected_signature = hmac.new(
            secret_bytes,
            msg=body_bytes, # body must be bytes
            digestmod=hashlib.sha1
        ).hexdigest()
        
        # The signature from Strava includes 'sha1=' prefix
        if signature and signature.startswith('sha1='):
            return hmac.compare_digest(signature.split('sha1=')[1], expected_signature)
        return False # Signature format incorrect or missing
    except Exception as e:
        print(f"Error during signature verification: {e}")
        return False

@functions_framework.http
def strava_webhook_handler(request):
    """
    HTTP Cloud Function that handles Strava webhook events.
    Args:
        request (flask.Request): The request object.
                                 <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    """
    print(f"Received request method: {request.method}")
    
    # --- Strava Webhook Subscription Validation (GET request) ---
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == STRAVA_VERIFY_TOKEN:
            print(f"Webhook subscription verified! Challenge: {challenge}")
            return json.dumps({'hub.challenge': challenge}), 200, {'Content-Type': 'application/json'}
        else:
            print(f"Webhook verification failed. Mode: {mode}, Token: {token}")
            return json.dumps({'error': 'Verification failed'}), 403, {'Content-Type': 'application/json'}

    # --- Strava Webhook Event Processing (POST request) ---
    elif request.method == 'POST':
        try:
            # For POST requests, get data from the request body
            # request.get_data() returns bytes, which is what hmac.new expects
            body_bytes = request.get_data()
            if not body_bytes:
                print("No body in POST request.")
                return json.dumps({'error': 'No body in request'}), 400, {'Content-Type': 'application/json'}

            payload = json.loads(body_bytes.decode('utf-8')) # Decode bytes to string, then load JSON
            print(f"Received Strava webhook payload: {json.dumps(payload, indent=2)}")

            # Verify subscription id for security
            subscription_id = payload.get('subscription_id')
            print(f"Received subscription ID: {subscription_id}")
            if not subscription_id or (subscription_id != int(STRAVA_SUBSCRIPTION_ID)):
                print("Invalid or missing subscription ID.")
                return json.dumps({'error': 'Invalid or missing subscription ID'}), 401, {'Content-Type': 'application/json'}

            # --- Your Core Script Logic Goes Here ---
            # This is where you integrate your existing Python script.
            # You'll parse the 'payload' to understand the event (e.g., new activity, updated activity).
            
            object_type = payload.get('object_type')
            aspect_type = payload.get('aspect_type')
            object_id = payload.get('object_id')
            owner_id = payload.get('owner_id')

            if object_type == 'activity' and aspect_type == 'create':
                print(f"New activity created! Activity ID: {object_id}, Owner ID: {owner_id}")
                # Call your original script's function here, passing relevant data
                # e.g., your_original_script_function(object_id, owner_id)
            elif object_type == 'activity' and aspect_type == 'update':
                print(f"Activity updated! Activity ID: {object_id}, Owner ID: {owner_id}, Updates: {payload.get('updates')}")
            elif object_type == 'athlete' and aspect_type == 'update':
                print(f"Athlete updated! Athlete ID: {object_id}, Updates: {payload.get('updates')}")
            else:
                print(f"Unhandled event type: Object Type={object_type}, Aspect Type={aspect_type}")
            # --- End of Core Script Logic Placeholder ---

            return json.dumps({'message': 'Webhook processed successfully'}), 200, {'Content-Type': 'application/json'}

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e} - Body: {request.get_data().decode('utf-8')}")
            return json.dumps({'error': 'Invalid JSON payload'}), 400, {'Content-Type': 'application/json'}
        except Exception as e:
            print(f"Unexpected error during POST request: {e}")
            return json.dumps({'error': 'Internal server error'}), 500, {'Content-Type': 'application/json'}
    else:
        print(f"Unsupported HTTP method: {request.method}")
        return json.dumps({'error': 'Method Not Allowed'}), 405, {'Content-Type': 'application/json'}