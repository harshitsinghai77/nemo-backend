FROM python:3.13-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get install -y --no-install-recommends curl \
    && apt-get install -y --no-install-recommends libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements.txt and app files into the container
COPY requirements.txt ./
COPY app/ ./app/
COPY main.py ./ 
COPY package_lambda.py ./

# Run the Python script package_lambda.py
CMD ["python", "package_lambda.py"]
