from backend.app import app
from backend.config import Config

if __name__ == '__main__':
    Config.init_dirs()
    app.run(host='0.0.0.0', port=5000, debug=True)