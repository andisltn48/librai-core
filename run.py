from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from config.database import db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/librai'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # max file 20mb

# Inisialisasi SQLAlchemy dengan app utama
db.init_app(app)

# Buat tabel database jika belum ada
with app.app_context():
    db.create_all()

# Serve file dokumen agar bisa didownload dari frontend
@app.route('/documents/<path:filename>')
def serve_document(filename):
    from flask import send_from_directory
    return send_from_directory('documents', filename)

# Import dan register blueprint setelah app dan db siap
from app.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=3007, host='0.0.0.0')