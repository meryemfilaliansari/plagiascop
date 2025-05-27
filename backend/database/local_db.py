"""
Module pour la gestion de la session SQLAlchemy.

Fournit une fonction pour obtenir une nouvelle session de base de données
connectée à la base de données SQLite du projet.
"""

from sqlalchemy.orm import sessionmaker
from backend.database.models import init_db

# Initialisation de la base de données et création du moteur SQLAlchemy
# Le moteur est créé une seule fois lors de l'importation de ce module
engine = init_db()

# Création de la fabrique de sessions
# Cette fabrique sera utilisée pour créer de nouvelles sessions
Session = sessionmaker(bind=engine)

def get_session():
    """
    Retourne une nouvelle session de base de données SQLAlchemy.

    Cette session est liée au moteur de base de données du projet.
    Il est crucial de fermer cette session après utilisation pour libérer
    les ressources (généralement dans un bloc finally).

    Returns:
        sqlalchemy.orm.Session: Une nouvelle session de base de données.
    """
    return Session()
