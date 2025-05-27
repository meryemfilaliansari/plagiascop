"""
Module pour les métriques de similarité et l'analyse de texte.

Contient la classe SimilarityAnalyzer pour prétraiter le texte,
calculer la similarité et identifier les sections correspondantes.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure NLTK data is downloaded (should be handled by setup.py)
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print("Téléchargement de 'punkt' pour SimilarityAnalyzer...")
    nltk.download('punkt')
except LookupError:
     print("Téléchargement de 'punkt' pour SimilarityAnalyzer...")
     nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    print("Téléchargement de 'stopwords' pour SimilarityAnalyzer...")
    nltk.download('stopwords')
except LookupError:
     print("Téléchargement de 'stopwords' pour SimilarityAnalyzer...")
     nltk.download('stopwords')


# Get French stopwords
stop_words_fr = set(stopwords.words('french'))


class SimilarityAnalyzer:
    """
    Analyseur de similarité pour comparer des textes.

    Fournit des méthodes pour prétraiter le texte, calculer la similarité,
    et trouver les sections correspondantes.
    """
    def __init__(self):
        """
        Initialise le SimilarityAnalyzer.
        """
        # Les stopwords et le stemmer peuvent être initialisés ici si nécessaire
        # self.stop_words = set(stopwords.words('french'))
        # self.stemmer = SnowballStemmer('french') # Si vous utilisez le stemming

    def split_into_sentences(self, text):
        """
        Divise un texte en une liste de phrases.

        Utilise NLTK pour une segmentation de phrases plus précise en français.

        Args:
            text (str): Le texte d'entrée à diviser.

        Returns:
            list[str]: Une liste de phrases extraites du texte.
        """
        if not text:
            return []
        # Utilise NLTK pour une meilleure segmentation de phrases
        return sent_tokenize(text, language='french')

    def preprocess_text(self, text):
        """
        Nettoie et tokenise le texte (minuscules, suppression ponctuation/stopwords).

        Args:
            text (str): Le texte d'entrée.

        Returns:
            list[str]: Liste des tokens prétraités.
        """
        if not text:
            return []
        # Convertir en minuscules
        text = text.lower()
        # Supprimer la ponctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Tokenisation
        tokens = word_tokenize(text, language='french')
        # Suppression des mots vides (stopwords)
        tokens = [word for word in tokens if word not in stop_words_fr]
        # Optionnel: ajouter le stemming ici si nécessaire
        # tokens = [self.stemmer.stem(w) for w in tokens]
        return tokens

    def jaccard_similarity(self, set1, set2):
        """
        Calcule la similarité de Jaccard entre deux ensembles de tokens.

        La similarité de Jaccard est le rapport de la taille de l'intersection
        sur la taille de l'union des deux ensembles.

        Args:
            set1 (set): Premier ensemble de tokens.
            set2 (set): Deuxième ensemble de tokens.

        Returns:
            float: Score de similarité de Jaccard (0.0 à 1.0). Retourne 0 si l'union est vide.
        """
        if not set1 and not set2:
            return 1.0 # Deux ensembles vides sont considérés comme identiques
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0.0

    def combined_similarity(self, text1, text2):
        """
        Calcule un score de similarité globale entre deux textes.

        Utilise la similarité de Jaccard sur les tokens prétraités.

        Args:
            text1 (str): Premier texte.
            text2 (str): Deuxième texte.

        Returns:
            float: Score de similarité (0.0 à 1.0).
        """
        print("DEBUG: Real combined_similarity called.")
        tokens1 = set(self.preprocess_text(text1))
        tokens2 = set(self.preprocess_text(text2))
        score = self.jaccard_similarity(tokens1, tokens2)
        print(f"DEBUG: Calculated similarity score: {score}")
        return score

    def find_matched_sections(self, text1, text2, sentence_similarity_threshold=0.5):
        """
        Trouve les sections (phrases) similaires entre deux textes.

        Compare chaque phrase du premier texte avec chaque phrase du deuxième texte
        en utilisant la similarité de Jaccard sur les tokens prétraités.

        Args:
            text1 (str): Premier texte (généralement le texte soumis).
            text2 (str): Deuxième texte (le document comparé).
            sentence_similarity_threshold (float): Seuil de similarité (0.0 à 1.0)
                                                   pour considérer deux phrases comme similaires.

        Returns:
            list[dict]: Liste de dictionnaires décrivant les sections correspondantes trouvées.
                        Chaque dict contient 'source_sentence' (phrase du texte1)
                        et 'matched_sentence' (phrase du texte2).
        """
        print("DEBUG: Real find_matched_sections called.")
        sentences1 = self.split_into_sentences(text1)
        sentences2 = self.split_into_sentences(text2)
        matched_sections = []

        # Simple comparaison phrase par phrase
        for sent1 in sentences1:
            sent1_tokens = set(self.preprocess_text(sent1))
            for sent2 in sentences2:
                sent2_tokens = set(self.preprocess_text(sent2))
                # Calcule la similarité entre les phrases
                sim_score = self.jaccard_similarity(sent1_tokens, sent2_tokens)

                if sim_score > sentence_similarity_threshold: # Si la similarité dépasse le seuil
                    matched_sections.append({
                        "source_sentence": sent1,
                        "matched_sentence": sent2,
                        "similarity": sim_score # Optionnel: inclure le score de similarité de la phrase
                    })
                    # Optionnel: arrêter après la première correspondance pour chaque phrase de text1
                    # break

        print(f"DEBUG: Found {len(matched_sections)} matched sections.")
        return matched_sections
