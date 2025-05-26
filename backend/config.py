import os
from pathlib import Path

class Config:
    # Chemins de base
    BASE_DIR = Path(__file__).parent.parent
    DATABASE_PATH = os.path.join(BASE_DIR, "plagiarism_db.sqlite")
    CACHE_DIR = os.path.join(BASE_DIR, "cache")
    
    # Paramètres de recherche
    EXTERNAL_SEARCH_TIMEOUT = 30  # secondes
    SIMILARITY_THRESHOLD = 0.7  # 70% de similarité considéré comme plagiat
    AI_DETECTION_MODEL = "roberta-base-openai-detector"
    
    # Paramètres Selenium
    CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
    CHROME_HEADLESS = True
    
    @staticmethod
    def init_dirs():
        """Initialise les répertoires nécessaires"""
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        db_dir = os.path.dirname(Config.DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)