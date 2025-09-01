# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create audio directory
RUN mkdir -p audio

# Expose ports
EXPOSE 1234 8080

# Create startup script
RUN echo '#!/bin/bash\n\
python backend.py &\n\
streamlit run frontend.py --server.port 8080 --server.address 0.0.0.0\n\
' > start_docker.sh && chmod +x start_docker.sh

# Start the application
CMD ["./start_docker.sh"]
