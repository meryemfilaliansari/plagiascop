import subprocess
import sys
import os
from pathlib import Path
from backend.config import Config

def install_requirements():
    print("Installation des dépendances...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def download_nltk_data():
    print("Téléchargement des données NLTK...")
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')

def setup_database():
    print("Initialisation de la base de données...")
    from backend.database.models import init_db
    engine = init_db()
    print(f"Base de données créée à: {Config.DATABASE_PATH}")

def check_chromedriver():
    print("Vérification de Chromedriver...")
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
    except Exception as e:
        print(f"Erreur Chromedriver: {str(e)}")
        print("Installez Chrome et Chromedriver manuellement si nécessaire")

def main():
    print("Configuration du système de détection de plagiat...")
    Config.init_dirs()
    install_requirements()
    download_nltk_data()
    setup_database()
    check_chromedriver()
    print("\nInstallation terminée! Exécutez 'python main.py' pour démarrer l'application.")

if __name__ == '__main__':
    main()