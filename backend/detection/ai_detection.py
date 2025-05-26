# File: backend/detection/ai_detection.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.config import Config
from typing import Tuple

class AIDetector:
    def __init__(self, ai_threshold: float = 0.85, uncertain_threshold: float = 0.5):
        """
        Initialise le détecteur IA avec des seuils configurables.

        Args:
            ai_threshold: Score de probabilité IA au-dessus duquel le verdict est "Probablement IA".
            uncertain_threshold: Score de probabilité IA au-dessus duquel le verdict est "Incertain"
                                 (et en dessous de ai_threshold).
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.ai_threshold = ai_threshold
        self.uncertain_threshold = uncertain_threshold
        self._load_model()

    def _load_model(self):
        try:
            # Utilise le modèle spécifié dans Config
            self.tokenizer = AutoTokenizer.from_pretrained(Config.AI_DETECTION_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(Config.AI_DETECTION_MODEL)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            raise ValueError(f"Erreur de chargement du modèle de détection IA: {str(e)}")

    def detect_ai_generated(self, text: str, max_length: int = 512) -> Tuple[float, str]:
        """Détecte si le texte est généré par IA et retourne un score de confiance"""
        if not text.strip():
            return 0.0, "Texte vide"

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
                padding="max_length"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Le modèle roberta-base-openai-detector a généralement 2 classes: 0 pour humain, 1 pour IA (fake)
                probs = torch.softmax(outputs.logits, dim=-1)
                human_prob = probs[0][0].item() # Probabilité d'être humain
                ai_prob = probs[0][1].item()    # Probabilité d'être IA (fake)

            confidence = ai_prob # Le score de confiance est la probabilité d'être IA

            # Utilise les seuils configurables
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
        """Analyse le texte par segments pour détecter les parties potentiellement générées par IA"""
        words = text.split()
        # Crée des segments en joignant les mots
        segments = [' '.join(words[i:i+segment_length]) for i in range(0, len(words), segment_length)]

        results = []
        for segment in segments:
            # Appelle detect_ai_generated pour chaque segment (utilise les seuils de l'instance)
            score, verdict = self.detect_ai_generated(segment)
            results.append({
                'text': segment,
                'ai_score': score,
                'verdict': verdict
            })

        # Calcule le score moyen et le verdict global
        avg_score = sum(r['ai_score'] for r in results) / len(results) if results else 0

        # Utilise les seuils configurables pour le verdict global
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
