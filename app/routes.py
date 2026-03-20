from flask import Blueprint, request, jsonify
from app.core_ai import ask_ai_fast

api_bp = Blueprint('api', __name__)

@api_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    user_input = data['query']
    try:
        result = ask_ai_fast(user_input)
        return jsonify({
            'response': str(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        