from flask import Flask
from flask_cors import CORS
from app.routes import api_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=3006, host='0.0.0.0')