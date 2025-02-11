# Use Debian Slim for a smaller but compatible image
FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc libffi-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y postgresql-client

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
