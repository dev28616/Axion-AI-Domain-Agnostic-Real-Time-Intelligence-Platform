FROM python:3.10-slim

WORKDIR /app

# Set the PYTHONPATH environment variable for correct module imports.
ENV PYTHONPATH=/app
# Prevent Hugging Face from trying to collect telemetry.
ENV HF_HUB_DISABLE_TELEMETRY=1
# Set the cache directory to our persistent volume.
ENV HF_HOME=/huggingface_cache
ENV TRANSFORMERS_CACHE=/huggingface_cache

# Install system dependencies, including curl for the healthcheck and Kafka tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    gnupg \
    && wget -qO - https://packages.confluent.io/deb/7.3/archive.key | gpg --dearmor -o /usr/share/keyrings/confluent-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/confluent-archive-keyring.gpg] https://packages.confluent.io/deb/7.3 stable main" > /etc/apt/sources.list.d/confluent.list \
    && apt-get update \
    && apt-get install -y confluent-kafka-tools \
    && rm -rf /var/lib/apt/lists/* \
    && pip install confluent-kafka[avro]

# Copy the requirements file.
COPY requirements.txt .

# Install all application dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . .

