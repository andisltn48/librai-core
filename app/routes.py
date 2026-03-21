from flask import Blueprint, request, jsonify
from app.core_ai import ask_ai_by_docs, ask_ai_by_internet
from app.file import upload_file, get_all_files, delete_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth import auth_register, auth_login
from config.database import Document

api_bp = Blueprint('api', __name__)

@api_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    user_input = data['query']
    try:
        # Ambil daftar file milik user ini
        user_files = Document.query.filter_by(user_id=user_id).all()
        allowed_filenames = [f.filename for f in user_files]
        
        result = ask_ai_by_docs(user_input, allowed_filenames=allowed_filenames)
        return jsonify({
            'response': str(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ask-internet', methods=['POST'])
@jwt_required()
def ask_by_internet():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    user_input = data['query']
    try:
        result = ask_ai_by_internet(user_input)
        return jsonify({
            'response': str(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    user_id = get_jwt_identity()
    try:
        result = upload_file(request, user_id)
        return result
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    print(f"DEBUG LIST_FILES: user_id={user_id}, type={type(user_id)}")
    try:
        result = get_all_files(user_id)
        return result
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/document/delete/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete(file_id):
    user_id = get_jwt_identity()
    try:
        return delete_file(file_id, user_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        return auth_register(request)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        return auth_login(request)
    except Exception as e:
        return jsonify({'error': str(e)}), 500