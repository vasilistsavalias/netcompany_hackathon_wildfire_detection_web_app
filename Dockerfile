# --- Stage 1: Build the Frontend (Node.js environment) ---
FROM node:18-alpine AS frontend-builder
WORKDIR /app/front_end

# Copy package.json and package-lock.json
COPY front_end/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the frontend source code
COPY front_end/ ./

# Build the frontend
RUN npm run build

# --- Stage 2: Set up the Backend (Python environment) ---
FROM python:3.11-slim AS backend-builder
WORKDIR /app

# Install PostgreSQL client libraries (needed for psycopg2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy the backend code
COPY machine_learning/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY machine_learning/ ./

# --- Stage 3: Final Image (Nginx to serve frontend, Python for backend) ---
FROM python:3.11-slim

# Install Nginx and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/front_end/dist /usr/share/nginx/html

# Copy the backend from the previous stage
COPY --from=backend-builder /app /app
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Configure Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Configure supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Expose ports
EXPOSE 80
EXPOSE 8080

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
