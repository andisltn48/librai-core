import os
from flask import jsonify, request
from werkzeug.utils import secure_filename
from config.database import db, Document

UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf'}

def validate(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and validate(file.filename):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        new_doc = Document(
            filename=filename,
            filepath=filepath,
            file_size=os.path.getsize(filepath)
        )
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Invalid file type'}), 400

def get_all_files():
    base_url = request.host_url.rstrip('/')
    files = Document.query.all()
    file_list = []
    for file in files:
        file_list.append({
            'id': file.id,
            'filename': file.filename,
            'filepath': file.filepath,
            'url_file': f'{base_url}/documents/{file.filename}',
            'created_at': file.created_at
        })
    return jsonify({'files': file_list}), 200