from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
from models import db, Image
import requests
import os

AI_MODEL_API_URL = "http://127.0.0.1:5001/predict"

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({'error': f'Error saving file: {str(e)}'}), 500

    try:
        with open(save_path, "rb") as img_file:
            response = requests.post(AI_MODEL_API_URL, files={"image": img_file})

        if response.status_code != 200:
            return jsonify({'error': f'AI Model failed with status code: {response.status_code}', 'details': response.text}), 500

        ai_result = response.json()
        prediction = ai_result.get("prediction", "unknown")

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error communicating with AI model: {str(e)}: {type(e).__name__} - {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error processing AI model response: {str(e)}'}), 500


    new_image = Image(filename=filename, path=save_path, ai_result=prediction)
    db.session.add(new_image)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback in case of database error
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({
        'id': new_image.id,
        'filename': new_image.filename,
        'path': new_image.path,
        'ai_result': new_image.ai_result
    }), 201