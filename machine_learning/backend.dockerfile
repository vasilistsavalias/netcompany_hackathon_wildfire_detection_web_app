
    FROM python:3.9-alpine AS builder-39
    WORKDIR /app/stage1
    
    COPY stage1/requirements-39.txt .
    RUN pip install --no-cache-dir -r requirements-39.txt
    
    FROM python:3.10-alpine AS builder-310
    WORKDIR /app/stage2
    
    RUN apk add --no-cache postgresql-dev gcc musl-dev
    
    COPY stage2/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . ./
    
    FROM python:3.10-alpine
    WORKDIR /app
    
    RUN apk add --no-cache postgresql-libs tzdata && \
        adduser -D appuser && \
        chown -R appuser /app
    
    COPY --from=builder-39 /app/stage1 /app
    COPY --from=builder-310 /app/stage2 /app
    ENV PATH=/home/appuser/.local/bin:$PATH
    
    ENV FLASK_APP=run.py
    ENV FLASK_RUN_HOST=0.0.0.0
    ENV FLASK_RUN_PORT=8080
    ENV TZ=UTC
    
    USER appuser
    
    EXPOSE 8080
    
    CMD ["flask", "run"]