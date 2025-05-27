"""
Module pour la détection de contenu généré par IA.

Utilise un modèle de transformeur pré-entraîné (roberta-base-openai-detector)
pour évaluer la probabilité qu'un texte ou des segments de texte soient
générés par IA.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.config import Config
from typing import Tuple

class AIDetector:
    """
    Détecteur de contenu généré par IA utilisant un modèle de transformeur.

    Charge un modèle spécifié et fournit des méthodes pour analyser
    des textes complets ou des segments.
    """
    def __init__(self, ai_threshold: float = 0.85, uncertain_threshold: float = 0.5):
        """
        Initialise le détecteur IA avec des seuils configurables pour les verdicts.

        Charge le modèle et le tokenizer spécifiés dans la configuration.

        Args:
            ai_threshold (float): Score de probabilité IA (entre 0 et 1) au-dessus duquel
                                  le verdict est "Probablement IA". Doit être supérieur à uncertain_threshold.
            uncertain_threshold (float): Score de probabilité IA (entre 0 et 1) au-dessus duquel
                                         le verdict est "Incertain" (et en dessous de ai_threshold).
                                         Doit être entre 0 et 1.

        Raises:
            ValueError: Si le modèle de détection IA ne peut pas être chargé.
        """
        # Détermine l'appareil à utiliser (GPU si disponible, sinon CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        # Stocke les seuils configurés
        self.ai_threshold = ai_threshold
        self.uncertain_threshold = uncertain_threshold
        # Charge le modèle et le tokenizer au démarrage
        self._load_model()
        print(f"AIDetector initialisé avec seuils: IA > {self.ai_threshold}, Incertain > {self.uncertain_threshold}")


    def _load_model(self):
        """
        Charge le tokenizer et le modèle de transformeur pré-entraîné
        spécifié dans Config.AI_DETECTION_MODEL.
        """
        print(f"Chargement du modèle de détection IA: {Config.AI_DETECTION_MODEL}...")
        try:
            # Charge le tokenizer et le modèle depuis Hugging Face Hub
            self.tokenizer = AutoTokenizer.from_pretrained(Config.AI_DETECTION_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(Config.AI_DETECTION_MODEL)
            # Déplace le modèle sur l'appareil sélectionné (CPU/GPU)
            self.model.to(self.device)
            # Met le modèle en mode évaluation (désactive dropout, etc.)
            self.model.eval()
            print("Modèle de détection IA chargé avec succès.")
        except Exception as e:
            print(f"Erreur de chargement du modèle de détection IA: {str(e)}")
            # Relève l'exception pour signaler l'échec du chargement
            raise ValueError(f"Erreur de chargement du modèle de détection IA: {str(e)}")

    def detect_ai_generated(self, text: str, max_length: int = 512) -> Tuple[float, str]:
        """
        Détecte si un segment de texte est généré par IA et retourne un score de confiance et un verdict.

        Utilise le modèle chargé pour prédire la probabilité que le texte soit "fake" (IA).

        Args:
            text (str): Le segment de texte à analyser.
            max_length (int): La longueur maximale (en tokens) pour la tokenisation du modèle.
                              Les textes plus longs seront tronqués.

        Returns:
            Tuple[float, str]: Un tuple contenant :
                               - float: Le score de probabilité IA (entre 0 et 1).
                               - str: Le verdict ("Probablement IA", "Incertain", "Probablement humain",
                                      "Texte vide", ou "Erreur d'analyse").
        """
        # Gère le cas du texte vide
        if not text.strip():
            return 0.0, "Texte vide"

        try:
            # Tokenisation et préparation des inputs pour le modèle
            inputs = self.tokenizer(
                text,
                return_tensors="pt", # Retourne des tenseurs PyTorch
                truncation=True,     # Tronque si le texte est plus long que max_length
                max_length=max_length,
                padding="max_length" # Padde si le texte est plus court que max_length
            ).to(self.device) # Déplace les inputs sur le même appareil que le modèle

            # Exécution du modèle en mode inférence (pas de calcul de gradients)
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Le modèle roberta-base-openai-detector a généralement 2 classes: 0 pour humain, 1 pour IA (fake)
                # Applique la fonction softmax pour obtenir des probabilités sur les logits de sortie
                probs = torch.softmax(outputs.logits, dim=-1)
                human_prob = probs[0][0].item() # Probabilité d'être humain (classe 0)
                ai_prob = probs[0][1].item()    # Probabilité d'être IA (fake) (classe 1)

            confidence = ai_prob # Le score de confiance est la probabilité d'être IA

            # Détermine le verdict basé sur les seuils configurables de l'instance
            if confidence > self.ai_threshold:
                verdict = "Probablement IA"
            elif confidence > self.uncertain_threshold:
                verdict = "Incertain"
            else:
                verdict = "Probablement humain"

            return confidence, verdict
        except Exception as e:
            print(f"Erreur lors de la détection IA: {str(e)}")
            return 0.0, "Erreur d'analyse"

    def analyze_text_segments(self, text: str, segment_length: int = 500) -> dict:
        """
        Analyse le texte complet en le divisant en segments et en détectant l'IA pour chaque segment.

        Calcule également un score moyen et un verdict global pour l'ensemble du texte
        basés sur les analyses de segments.

        Args:
            text (str): Le texte complet à analyser.
            segment_length (int): La taille (en mots) de chaque segment pour l'analyse.

        Returns:
            dict: Un dictionnaire contenant :
                  - 'segments' (list): Liste des résultats pour chaque segment (texte, score IA, verdict).
                  - 'average_score' (float): Score IA moyen sur tous les segments.
                  - 'overall_verdict' (str): Verdict global pour l'ensemble du texte
                                             ("Probablement IA", "Incertain", "Probablement humain",
                                             ou basé sur le score moyen).
        """
        # Divise le texte en mots
        words = text.split()
        # Crée des segments en joignant les mots par blocs de segment_length
        segments = [' '.join(words[i:i+segment_length]) for i in range(0, len(words), segment_length)]

        results = []
        # Analyse chaque segment individuellement
        for segment in segments:
            # Appelle detect_ai_generated pour chaque segment (utilise les seuils de l'instance)
            score, verdict = self.detect_ai_generated(segment)
            results.append({
                'text': segment,
                'ai_score': score,
                'verdict': verdict
            })

        # Calcule le score moyen sur tous les segments
        avg_score = sum(r['ai_score'] for r in results) / len(results) if results else 0

        # Détermine le verdict global basé sur le score moyen et les seuils configurables
        if avg_score > self.ai_threshold:
            overall_verdict = "Probablement IA"
        elif avg_score > self.uncertain_threshold:
            overall_verdict = "Incertain"
        else:
            overall_verdict = "Probablement humain"

        return {
            'segments': results,
            'average_score': avg_score,
            'overall_verdict': overall_verdict
        }
