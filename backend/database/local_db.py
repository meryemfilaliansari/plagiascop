from sqlalchemy.orm import sessionmaker
from backend.database.models import init_db

# Initialisation de la base de données
engine = init_db()

# Création de la fonction get_session
Session = sessionmaker(bind=engine)

def get_session():
    """Retourne une nouvelle session de base de données"""
    return Session() 