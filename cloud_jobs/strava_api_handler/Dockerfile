FROM python:3.11-slim

ENV APP_HOME=/app
ENV PYTHONUNBUFFERED=1

WORKDIR $APP_HOME

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Use CMD only, which allows arguments to be passed correctly
ENTRYPOINT ["python", "main.py"]