"""
Module de configuration pour l'application PlagiaScope.

Définit les chemins des répertoires pour les données, le cache et la base de données,
ainsi que le nom du modèle de détection IA à utiliser.
"""

import os

class Config:
    """
    Classe de configuration contenant les chemins et paramètres globaux.
    """
    # Chemin absolu du répertoire de base du projet (un niveau au-dessus du répertoire backend)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Chemin du répertoire pour stocker les données (base de données, etc.)
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    # Chemin du répertoire pour le cache (fichiers téléchargés temporairement)
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    # Chemin du répertoire pour la base de données
    DATABASE_DIR = os.path.join(DATA_DIR, 'database')
    # Chemin complet du fichier de base de données SQLite
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'plagiarism_db.sqlite')
    # Nom du modèle de détection IA à utiliser (nom du modèle Hugging Face)
    AI_DETECTION_MODEL = "roberta-base-openai-detector"


    @staticmethod
    def init_dirs():
        """
        Initialise les répertoires nécessaires (DATA_DIR, CACHE_DIR, DATABASE_DIR)
        si ils n'existent pas.
        """
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        os.makedirs(Config.DATABASE_DIR, exist_ok=True)
        print(f"Répertoires initialisés: {Config.DATA_DIR}, {Config.CACHE_DIR}, {Config.DATABASE_DIR}")

