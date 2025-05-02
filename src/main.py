import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.reservation import db # Changed from user model
from src.routes.reservation import reservation_bp
from src.routes.chat import chat_bp
from src.routes.whatsapp import whatsapp_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key_change_me') # Use env var
app.register_blueprint(reservation_bp, url_prefix="/api/reservations")
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(whatsapp_bp, url_prefix="/api/whatsapp")
# Database configuration using PostgreSQL
db_user = os.getenv('DB_USER', 'pila_user')
db_password = os.getenv('DB_PASSWORD', 'pila_password')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'pila_reservations')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all() # Creates the 'reservations' table if it doesn't exist

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # Return API status or info if index.html is not found
            return jsonify({"status": "API is running", "docs": "/api/reservations"}), 200


if __name__ == '__main__':
    # Use environment variable for port or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # Set debug=False for production/testing

