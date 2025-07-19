FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY scripts/ ./scripts/

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Make main script executable
RUN chmod +x /app/scripts/main.py

# Set Python path
ENV PYTHONPATH=/app/scripts

# Default command
CMD ["python", "/app/scripts/main.py"]
