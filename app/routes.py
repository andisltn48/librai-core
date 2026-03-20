from flask import Blueprint, request, jsonify
from app.core_ai import ask_ai_by_docs, ask_ai_by_internet
from app.upload import upload_file

api_bp = Blueprint('api', __name__)

@api_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    user_input = data['query']
    try:
        result = ask_ai_by_docs(user_input)
        return jsonify({
            'response': str(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ask-internet', methods=['POST'])
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
def upload():
    try:
        result = upload_file(request)
        return result
    except Exception as e:
        return jsonify({'error': str(e)}), 500