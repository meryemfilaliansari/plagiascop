"""
Point d'entrée principal pour lancer l'application PlagiaScope.

Ce script initialise les répertoires nécessaires et démarre le serveur web Flask.
"""

from backend.app import app
from backend.config import Config

if __name__ == '__main__':
    # Initialise les répertoires de données et de cache définis dans Config
    Config.init_dirs()
    # Démarre l'application Flask
    # host='0.0.0.0' rend l'application accessible depuis votre réseau local
    # port=5000 est le port par défaut
    # debug=True active le mode débogage (utile pendant le développement)
    app.run(host='0.0.0.0', port=5000, debug=True)
