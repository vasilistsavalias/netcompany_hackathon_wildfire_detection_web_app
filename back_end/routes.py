from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
from models import db, Image
import os

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Save the file
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
    file.save(save_path)

    # Create database entry
    new_image = Image(
        filename=filename,
        path=save_path
    )
    db.session.add(new_image)
    db.session.commit()

    return jsonify({
        'id': new_image.id,
        'filename': new_image.filename,
        'path': new_image.path,
        'ai_result': new_image.ai_result
    }), 201

@app.route('/api/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([{
        'id': img.id,
        'filename': img.filename,
        'ai_result': img.ai_result
    } for img in images])