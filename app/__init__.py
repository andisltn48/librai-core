from flask import Flask
from flask_cors import CORS

def create_app():
    # 1. Inisialisasi objek Flask
    app = Flask(__name__)
    
    # 2. Aktifkan CORS (agar API bisa diakses dari luar)
    CORS(app)
    
    # 3. Import dan Registrasi Blueprint (Route) di dalam fungsi 
    # untuk menghindari 'Circular Import' (Error saling panggil)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app