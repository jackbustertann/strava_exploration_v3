import os
import base64
import json
import sys
from cloudevents.http import CloudEvent

def process_pubsub_message():
    """
    Processes a Pub/Sub message received via Eventarc.
    """
    print("Cloud Run Job 'strava-api-handler' started.")

    try:
        # Read the raw JSON string received from eventarc.
        event_data_raw = sys.stdin.read()

        # Exit script early if no data is received
        if not event_data_raw:
            print("No CloudEvent object received. Exiting.")
            return

        # Parse the raw JSON string into a CloudEvent object
        event = CloudEvent(json.loads(event_data_raw))

        # Extract CloudEvent attributes
        event_id = event["id"]
        event_source = event["source"] # note: this will contain the Pub/Sub topic path
        event_type = event["type"]

        print(f"Received CloudEvent object: (ID: {event_id}, Type: {event_type}, Source: {event_source})")

        # The Pub/Sub message content is in the 'data' attribute of the CloudEvent.
        # This 'data' attribute itself contains the Pub/Sub message structure.
        pubsub_message = event['data'].get('message', {})
        pubsub_data_b64 = pubsub_message.get('data')
        pubsub_attributes = pubsub_message.get('attributes', {})
        publish_time = pubsub_message.get('publishTime')
        message_id = pubsub_message.get('messageId')

        print(f"Pub/Sub Message ID: {message_id}")
        print(f"Pub/Sub Publish Time: {publish_time}")
        print(f"Pub/Sub Attributes: {pubsub_attributes}")
        print(f"Pub/Sub Data (base64 encoded): {pubsub_data_b64}")

        if pubsub_data_b64:
            try:
                # Decode Pub/Sub message data from base64
                decoded_data = base64.b64decode(pubsub_data_b64).decode('utf-8')
                print(f"Pub/Sub Data (decoded): {decoded_data}")

                # Attempt to parse decoded Pub/Sub message to JSON
                try:
                    json_data = json.loads(decoded_data)
                    print("Successfully parsed Pub/Sub message to JSON.")
                except json.JSONDecodeError:
                    print(f"Error parsing Pub/Sub message to JSON.")

            except Exception as e:
                print(f"Error decoding Pub/Sub data from base64: {e}")
        else:
            print("No 'data' field found in Pub/Sub message.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    process_pubsub_message()