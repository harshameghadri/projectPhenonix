# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create data directory
RUN mkdir -p data

# Copy sample data
COPY data/ data/

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PROVIDER=ollama
ENV EMBEDDING_PROVIDER=local
ENV CHROMA_DB_PATH=./db
ENV BACKEND_HOST=0.0.0.0
ENV BACKEND_PORT=8000

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]