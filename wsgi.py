# wsgi.py
from src.main import app

if __name__ == "__main__":
    # Esta parte é opcional, usada apenas se executar 'python wsgi.py' localmente
    app.run()
