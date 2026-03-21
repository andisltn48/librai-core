from config.database import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import jsonify

def validate_user(username, password):
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    

def auth_register(request):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if validate_user(username, password):
        return validate_user(username, password)
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 200

def auth_login(request):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if validate_user(username, password):
        return validate_user(username, password)
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    print(f"DEBUG LOGIN: user_id={user.id}, token_identity={str(user.id)}")
    return jsonify({'access_token': access_token}), 200
    