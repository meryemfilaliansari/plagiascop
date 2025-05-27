"""
Script de configuration initiale pour PlagiaScope.

Ce script gère l'installation des dépendances, le téléchargement des données NLTK,
l'initialisation de la base de données et la vérification de Chromedriver.
Il doit être exécuté une fois après le clonage du dépôt.
"""

import subprocess
import sys
import os
from pathlib import Path
from backend.config import Config

def install_requirements():
    """
    Installe les dépendances Python listées dans requirements.txt en utilisant pip.

    Raises:
        subprocess.CalledProcessError: Si l'installation échoue.
    """
    print("Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dépendances installées avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation des dépendances: {e}")
        print("Veuillez vous assurer que pip est installé et que requirements.txt est présent.")
        raise

def download_nltk_data():
    """
    Télécharge les données NLTK nécessaires ('punkt' pour la segmentation de phrases
    et 'stopwords' pour la suppression des mots vides).

    Ces données sont requises par le module de comparaison locale.
    """
    print("Téléchargement des données NLTK...")
    try:
        import nltk
        # Tente de trouver les données, les télécharge si elles ne sont pas présentes
        try:
            nltk.data.find('tokenizers/punkt')
        except nltk.downloader.DownloadError:
            print("Téléchargement de 'punkt'...")
            nltk.download('punkt')
        except LookupError:
             print("Téléchargement de 'punkt'...")
             nltk.download('punkt')

        try:
            nltk.data.find('corpora/stopwords')
        except nltk.downloader.DownloadError:
            print("Téléchargement de 'stopwords'...")
            nltk.download('stopwords')
        except LookupError:
             print("Téléchargement de 'stopwords'...")
             nltk.download('stopwords')

        print("Données NLTK vérifiées/téléchargées.")
    except ImportError:
        print("Erreur: NLTK n'est pas installé. Veuillez exécuter 'pip install -r requirements.txt'.")
    except Exception as e:
        print(f"Erreur lors du téléchargement des données NLTK: {e}")


def setup_database():
    """
    Initialise la base de données SQLite si elle n'existe pas.

    Crée le fichier de base de données et les tables définies dans models.py.
    """
    print("Initialisation de la base de données...")
    try:
        from backend.database.models import init_db
        engine = init_db()
        print(f"Base de données créée ou déjà existante à: {Config.DATABASE_PATH}")
    except ImportError:
         print("Erreur: Les modules de base de données ne peuvent pas être importés. Assurez-vous que les dépendances sont installées.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")


def check_chromedriver():
    """
    Vérifie et installe Chromedriver automatiquement si possible en utilisant
    chromedriver-autoinstaller.

    Note: Cette étape peut échouer selon la configuration du système
    et la version de Chrome. L'utilisation de SerpApi réduit la dépendance
    à Selenium pour la recherche, mais Selenium peut être utilisé pour le scraping
    de contenu des URLs trouvées. Si cette étape échoue et que vous utilisez Selenium
    pour le scraping, vous devrez installer Chromedriver manuellement.
    """
    print("Vérification de Chromedriver...")
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        print("Chromedriver vérifié/installé automatiquement.")
    except ImportError:
        print("Avertissement: chromedriver-autoinstaller n'est pas installé. Selenium pourrait ne pas fonctionner sans Chromedriver.")
    except Exception as e:
        print(f"Avertissement: Erreur lors de l'installation automatique de Chromedriver: {str(e)}")
        print("Installez Chrome et Chromedriver manuellement si nécessaire et configurez le chemin dans external_search.py si vous utilisez Selenium pour le scraping.")

def main():
    """
    Exécute toutes les étapes de configuration du projet dans l'ordre.
    """
    print("Configuration du système de détection de plagiat PlagiaScope...")
    # Initialise les répertoires nécessaires en premier
    Config.init_dirs()
    # Installe les dépendances
    install_requirements()
    # Télécharge les données NLTK
    download_nltk_data()
    # Initialise la base de données
    setup_database()
    # Vérifie Chromedriver (optionnel selon l'utilisation de Selenium)
    check_chromedriver()
    print("\nInstallation et configuration terminées! Exécutez 'python main.py' pour démarrer l'application.")

if __name__ == '__main__':
    main()
