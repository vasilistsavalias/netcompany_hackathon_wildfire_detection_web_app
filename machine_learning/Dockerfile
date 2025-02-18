FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies including OpenCV requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    gfortran \
    libhdf5-dev \
    libopenblas-dev \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create a non-root user
RUN useradd -m appuser

# Create necessary directories with correct permissions *AFTER* creating the user
RUN mkdir -p /app/uploads /app/processed_images \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    && chmod 1777 /app/uploads /app/processed_images

# Switch to the non-root user
USER appuser

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Expose the port
EXPOSE 8080

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "run:app"]