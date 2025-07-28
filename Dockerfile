FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY process_pdfs.py .

# Set environment variables
ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output

# Create directories
RUN mkdir -p /app/input /app/output

# Set the entrypoint
ENTRYPOINT ["python", "process_pdfs.py"]