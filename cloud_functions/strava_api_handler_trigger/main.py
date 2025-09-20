import json
from google.cloud import run_v2

def trigger_strava_job(event, context):
    """Cloud Function to process Pub/Sub messages
    Args:
        event (dict): Raw Pub/Sub message
        context (google.cloud.functions.Context): Event metadata
    """

    print(f"Received Pub/Sub message (ID: {context.event_id})")
    
    # Convert the message object to a JSON string
    pubsub_message_string = json.dumps(event)

    print(f"Pub/Sub message content: {pubsub_message_string}")

    try:
        # Initiate the Cloud Run client
        client = run_v2.JobsClient()

        # Construct the job execution request
        PROJECT_ID = "strava-exploration-v2"
        LOCATION = "us-central1"
        JOB_NAME = "strava-api-handler"

        request = run_v2.RunJobRequest(
            name=f"projects/{PROJECT_ID}/locations/{LOCATION}/jobs/{JOB_NAME}",
            overrides=run_v2.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.RunJobRequest.Overrides.ContainerOverride(
                        args=[pubsub_message_string],
                    )
                ]
            )
        )

        # Start the job execution
        client.run_job(request=request)
        print(f"Successfully started Cloud Run job '{JOB_NAME}'")

    except Exception as e:
        print(f"An unexpected error occurred while starting the job: {e}")
        raise e