import base64
import json
import sys

def process_pubsub_message():
    """
    Processes a Pub/Sub message received as a command-line argument.
    """
    print("Cloud Run Job 'strava-api-handler' started.")

    try:
        # Check if a command-line argument was passed
        if len(sys.argv) < 2:
            print("No message data received. Exiting.")
            return

        # Extract the Pub/Sub message data from the command-line argument
        pubsub_message_string = sys.argv[1]
        
        # Parse the JSON string back into a Python object
        pubsub_message_json = json.loads(pubsub_message_string)

        # Now you can access all the message attributes
        pubsub_data_b64 = pubsub_message_json.get('data')
        message_id = pubsub_message_json.get('message_id')
        pubsub_publish_time = pubsub_message_json.get('publish_time')

        print(f"Pub/Sub Message: ID: {message_id}, Publish Time: {pubsub_publish_time}")
        
        if pubsub_data_b64:
            try:
                # Attempt to decode Pub/Sub message data from base64
                pubsub_data_decoded = base64.b64decode(pubsub_data_b64).decode('utf-8')
                print(f"Pub/Sub Data (decoded): {pubsub_data_decoded}")

                # Attempt to parse Pub/Sub message data to JSON
                try:
                    pubsub_data_json = json.loads(pubsub_data_decoded)
                    print("Successfully parsed Pub/Sub message data to JSON.")
                    return
                except json.JSONDecodeError:
                    print(f"Error parsing Pub/Sub message data to JSON.")

            except Exception as e:
                print(f"Error decoding Pub/Sub message data from base64: {e}")
        else:
            print("No 'data' field found in Pub/Sub message.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    process_pubsub_message()