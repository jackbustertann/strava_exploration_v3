FROM python:3.11-slim

# Set environment variables for non-buffered output (important for Cloud Run logs)
ENV PYTHONUNBUFFERED=1 \
    # Set the working directory inside the container
    APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Command to run the Cloud Function using functions-framework.
# --target strava_webhook_handler specifies the function to execute from main.py.
CMD ["functions-framework", "--target", "strava_webhook_handler"]