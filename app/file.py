import os
from flask import jsonify, request
from werkzeug.utils import secure_filename
from config.database import db, Document
from app.core_ai import add_to_chroma, delete_from_chroma

UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf'}

def validate(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request, user_id):
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
            file_size=os.path.getsize(filepath),
            user_id=user_id
        )
        db.session.add(new_doc)
        db.session.commit()
        
        # Sinkronisasi ke ChromaDB untuk RAG
        add_to_chroma(filepath, filename)
        
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Invalid file type'}), 400

def get_all_files(user_id):
    base_url = request.host_url.rstrip('/')
    # Filter dokumen berdasarkan user_id agar tiap user hanya melihat miliknya sendiri
    print(user_id)
    files = Document.query.filter_by(user_id=user_id).all()
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

def delete_file(file_id, user_id):
    # Pastikan file yang dihapus milik user yang sedang login
    file = Document.query.filter_by(id=file_id, user_id=user_id).first()
    if not file:
        return jsonify({'error': 'File not found or unauthorized'}), 404
    
    try:
        if os.path.exists(file.filepath):
            os.remove(file.filepath)
        
        # Hapus juga dari ChromaDB
        delete_from_chroma(file.filename)
        
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500