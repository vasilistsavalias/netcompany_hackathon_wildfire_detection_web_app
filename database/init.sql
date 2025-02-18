-- database/init.sql
CREATE TABLE IF NOT EXISTS image_result (
    id SERIAL PRIMARY KEY,
    original_filename VARCHAR(255),
    image_path VARCHAR(255),
    processed_image_path VARCHAR(255),
    yolo_detections TEXT,
    cnn_probability FLOAT,
    processing_time FLOAT,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    model_type VARCHAR(50)
);