from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import numpy as np
import hashlib
import re
from collections import defaultdict
from difflib import SequenceMatcher

class SimilarityAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        def sent_tokenize(self, text):
            """Tokenize le texte en phrases en utilisant NLTK"""
            return sent_tokenize(text)
    
    def calculate_cosine_similarity(self, text1, text2):
        """Calcule la similarité cosinus entre deux textes"""
        tfidf = self.vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    
    def find_matched_sections(self, text1, text2, threshold=0.7):
        """Trouve les sections similaires entre deux textes"""
        sentences1 = sent_tokenize(text1)
        sentences2 = sent_tokenize(text2)
        
        matched_sections = []
        for i, s1 in enumerate(sentences1):
            for j, s2 in enumerate(sentences2):
                similarity = self.calculate_cosine_similarity(s1, s2)
                if similarity >= threshold:
                    matched_sections.append({
                        'source_sentence': s1,
                        'matched_sentence': s2,
                        'similarity': similarity,
                        'source_position': i,
                        'matched_position': j
                    })
        
        return matched_sections
    
    def fingerprint_algorithm(self, text, k=5):
        """Implémentation de l'algorithme de fingerprint pour détection de copie"""
        words = re.findall(r'\w+', text.lower())
        fingerprints = set()
        
        for i in range(len(words) - k + 1):
            kgram = ' '.join(words[i:i+k])
            hash_val = hashlib.md5(kgram.encode()).hexdigest()
            fingerprints.add(hash_val)
        
        return fingerprints
    
    def fingerprint_similarity(self, text1, text2):
        """Calcule la similarité basée sur les fingerprints"""
        fp1 = self.fingerprint_algorithm(text1)
        fp2 = self.fingerprint_algorithm(text2)
        
        if not fp1 or not fp2:
            return 0.0
        
        intersection = fp1 & fp2
        union = fp1 | fp2
        return len(intersection) / len(union)
    
    def sequence_matcher_ratio(self, text1, text2):
        """Utilise difflib.SequenceMatcher pour une comparaison précise"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def combined_similarity(self, text1, text2):
        """Combinaison de plusieurs méthodes pour une évaluation robuste"""
        cosine = self.calculate_cosine_similarity(text1, text2)
        fingerprint = self.fingerprint_similarity(text1, text2)
        sequence = self.sequence_matcher_ratio(text1, text2)
        
        # Poids personnalisés pour chaque méthode
        return 0.5 * cosine + 0.3 * fingerprint + 0.2 * sequence