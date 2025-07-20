FROM python:3.11-slim

ENV APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Command to run the Cloud Function using functions-framework.
# --target strava_webhook_handler specifies the function to execute from main.py.
CMD ["functions-framework", "--target", "strava_webhook_handler"]