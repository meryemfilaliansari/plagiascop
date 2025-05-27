"""
Définit les modèles de base de données pour PlagiaScope en utilisant SQLAlchemy.

Inclut les modèles pour les documents stockés (Document) et les résultats
de comparaison (ComparisonResult).
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import Config
import os

# Base déclarative pour les modèles
# Tous les modèles de base de données hériteront de cette classe
Base = declarative_base()

class Document(Base):
    """
    Modèle représentant un document analysé stocké dans la base de données locale.

    Chaque instance de cette classe correspond à une ligne dans la table 'documents'.
    """
    __tablename__ = 'documents' # Nom de la table dans la base de données

    id = Column(Integer, primary_key=True) # Clé primaire auto-incrémentée
    title = Column(String(200), nullable=False) # Titre du document (chaîne de max 200 caractères, non nul)
    content = Column(Text, nullable=False) # Contenu complet du document (texte long, non nul)
    author = Column(String(100)) # Auteur du document (chaîne de max 100 caractères, peut être nul)
    hash = Column(String(64), unique=True)  # SHA-256 hash du contenu pour identifier les documents uniques
    created_at = Column(DateTime, default=datetime.utcnow) # Timestamp de création (par défaut: heure actuelle UTC)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Timestamp de dernière mise à jour

    def __repr__(self):
        """
        Représentation string de l'objet Document pour le débogage.
        """
        return f"<Document(id={self.id}, title='{self.title}', hash='{self.hash[:8]}...')>"

class ComparisonResult(Base):
    """
    Modèle représentant le résultat d'une comparaison entre un document
    analysé et une source (locale ou externe).

    Chaque instance correspond à une ligne dans la table 'comparison_results'.
    """
    __tablename__ = 'comparison_results' # Nom de la table

    id = Column(Integer, primary_key=True) # Clé primaire
    doc_id = Column(Integer, nullable=False) # ID du document analysé (clé étrangère implicite vers Document.id)
    compared_doc_id = Column(Integer) # ID du document local comparé (si applicable, peut être nul)
    compared_url = Column(String(500)) # URL de la source externe comparée (si applicable, peut être nulle)
    similarity_score = Column(Integer, nullable=False) # Score de similarité en pourcentage (0-100), non nul
    matched_sections = Column(Text) # Sections correspondantes (stockées en JSON string), peut être nul
    detection_method = Column(String(50)) # Méthode de détection ('local' ou 'external'), non nul
    is_ai_generated = Column(Integer)  # Verdict IA pour cette correspondance (0: no, 1: yes, 2: uncertain), peut être nul
    created_at = Column(DateTime, default=datetime.utcnow) # Timestamp de création

    def __repr__(self):
        """
        Représentation string de l'objet ComparisonResult pour le débogage.
        """
        source = f"Local #{self.compared_doc_id}" if self.compared_doc_id else self.compared_url
        return f"<ComparisonResult(id={self.id}, doc_id={self.doc_id}, source='{source}', score={self.similarity_score}%)>"


def init_db():
    """
    Initialise la base de données SQLite et crée les tables (documents, comparison_results)
    si elles n'existent pas déjà.

    Utilise le chemin de base de données spécifié dans Config.

    Returns:
        sqlalchemy.engine.Engine: Le moteur de base de données SQLAlchemy connecté.
    """
    # Création du répertoire de la base de données si nécessaire
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

    # Création du moteur SQLAlchemy
    engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')
    # Crée toutes les tables définies par Base.metadata si elles n'existent pas
    Base.metadata.create_all(engine)
    print(f"Base de données initialisée ou déjà existante à: {Config.DATABASE_PATH}")
    return engine

# Note: get_session est défini dans local_db.py et utilise le moteur créé ici.
