import re
import hashlib
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

nltk.download('punkt')
nltk.download('stopwords')

class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('french'))
        self.stemmer = SnowballStemmer('french')

    def preprocess_text(self, text):
        """Nettoyage et prétraitement du texte"""
        # Convertir en minuscules
        text = text.lower()
        # Supprimer les caractères spéciaux et les nombres
        text = re.sub(r'[^a-zéèêëàâäôöûüç\s]', '', text)
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize_and_stem(self, text):
        """Tokenisation et stemming"""
        words = word_tokenize(text)
        filtered_words = [self.stemmer.stem(w) for w in words if w not in self.stop_words]
        return filtered_words

    def calculate_text_hash(self, text):
        """Calculer un hash unique pour le texte"""
        processed_text = self.preprocess_text(text)
        return hashlib.sha256(processed_text.encode('utf-8')).hexdigest()

    def extract_key_phrases(self, text, num_phrases=5):
        """Extraire des phrases clés pour la recherche"""
        sentences = sent_tokenize(text)
        # Simple méthode basée sur la longueur et les mots clés
        scored_sentences = []
        for sent in sentences:
            words = [w for w in word_tokenize(sent.lower()) if w.isalpha()]
            score = len(words) * 0.5  # Poids pour la longueur
            if any(kw in words for kw in ['définir', 'conclusion', 'résultat', 'méthode']):
                score += 2  # Bonus pour les mots clés académiques
            scored_sentences.append((score, sent))
        
        # Trier par score et retourner les meilleures
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        return [s[1] for s in scored_sentences[:num_phrases]]