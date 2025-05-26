# File: backend/detection/local_comparison.py
# Need imports for database interaction
from backend.database.models import ComparisonResult, Document
from backend.database.local_db import get_session # Import get_session

# Need imports for similarity calculation if not already there
# from backend.detection.similarity_metrics import SimilarityAnalyzer # Remove if defined here

import json # Need json for serializing matched_sections
from datetime import datetime # Need datetime for created_at
import random # Import random for simulating scores (can be removed later)
import re # Import re for sentence splitting

# Import NLTK components
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string

# Ensure NLTK data is downloaded (should be handled by setup.py)
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')

# Get French stopwords
stop_words_fr = set(stopwords.words('french'))

class LocalComparator:
    def __init__(self):
        self.similarity_analyzer = SimilarityAnalyzer()
        # Maybe load local documents here or have a method to do so
        # self.local_documents = self._load_local_documents() # Placeholder

    def find_similar_documents(self, text, doc_id):
        """
        Compares the input text against documents in the local database
        and returns a list of matches.
        """
        print(f"DEBUG: Starting local comparison for doc_id {doc_id}...")
        session = get_session()
        matches = []
        try:
            # Query all documents except the one being analyzed
            other_docs = session.query(Document).filter(Document.id != doc_id).all()
            print(f"DEBUG: Found {len(other_docs)} other documents in local database.")

            for other_doc in other_docs:
                print(f"DEBUG: Comparing with local document ID {other_doc.id} - '{other_doc.title}'")
                # Use the placeholder similarity calculation
                # NOTE: This needs a real implementation for actual comparison
                score = self.similarity_analyzer.combined_similarity(text, other_doc.content)

                # Check if similarity score is above a threshold
                # Adjust threshold based on your needs and the chosen similarity metric
                if score > 0.1: # Example threshold - adjust as needed
                    print(f"DEBUG: Potential match found with local document ID {other_doc.id}, score: {score}")
                    # Use the placeholder for finding matched sections
                    # NOTE: This needs a real implementation to find actual sections
                    sections = self.similarity_analyzer.find_matched_sections(text, other_doc.content)

                    matches.append({
                        'compared_doc_id': other_doc.id,
                        'title': other_doc.title,
                        'author': other_doc.author,
                        'similarity': score, # Keep as float for now, convert to int percentage when saving
                        'matched_sections': sections # This will be [] with the placeholder
                    })
                else:
                    print(f"DEBUG: No significant similarity with local document ID {other_doc.id}, score: {score}")

        except Exception as e:
            print(f"ERROR: An error occurred during local comparison: {e}")
            # Depending on desired behavior, you might want to re-raise or return empty list
            return [] # Return empty list on error
        finally:
            session.close() # Ensure session is closed

        print(f"DEBUG: Local comparison completed. Found {len(matches)} potential local matches.")
        return matches

    def save_comparison_results(self, doc_id, results_list, is_ai_generated, session):
        """Saves comparison results to the database."""
        print(f"DEBUG: Saving {len(results_list)} comparison results for doc_id {doc_id}")
        for result in results_list:
            # Determine detection method and populate fields based on result structure
            compared_doc_id = result.get('compared_doc_id')
            compared_url = result.get('url')
            detection_method = 'local' if compared_doc_id is not None else 'external'

            # Ensure similarity is an integer percentage
            # The results_list seems to contain similarity as a float (e.g., 0.7)
            similarity_score = int(result.get('similarity', 0) * 100)

            # Serialize matched_sections to a JSON string
            matched_sections_data = result.get('matched_sections', [])
            # Use json.dumps to correctly serialize the list/dict to a JSON string
            matched_sections_json_str = json.dumps(matched_sections_data)

            comparison = ComparisonResult(
                doc_id=doc_id,
                compared_doc_id=compared_doc_id,
                compared_url=compared_url,
                similarity_score=similarity_score,
                matched_sections=matched_sections_json_str, # Saved as JSON string now
                detection_method=detection_method,
                # is_ai_generated seems to be applied to the whole analysis run,
                # not per comparison result. This might need review based on
                # how AI detection results are structured and saved.
                # For now, applying the overall AI verdict to each comparison result.
                is_ai_generated=is_ai_generated,
                created_at=datetime.utcnow() # Add creation timestamp
            )
            session.add(comparison)

        # session.commit() # Commit is handled in app.py
        print("DEBUG: Comparison results prepared for saving.")

    # Add other methods for local comparison as needed
    # For example, a method to add documents to the local corpus for comparison
    # def add_document_to_corpus(self, doc): pass
    # def _load_local_documents(self): pass


# Add a placeholder for SimilarityAnalyzer if it's not in a separate file
# In a real project, this would be in backend/detection/similarity_metrics.py
class SimilarityAnalyzer:
    def split_into_sentences(self, text):
        # Use NLTK for better sentence splitting
        return sent_tokenize(text, language='french')

    def preprocess_text(self, text):
        # Lowercase, remove punctuation, tokenize, remove stopwords
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(text, language='french')
        tokens = [word for word in tokens if word not in stop_words_fr]
        return tokens

    def jaccard_similarity(self, set1, set2):
        # Calculate Jaccard similarity between two sets of tokens
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    def combined_similarity(self, text1, text2):
        # Calculate similarity using Jaccard on preprocessed text
        print("DEBUG: Real combined_similarity called.")
        tokens1 = set(self.preprocess_text(text1))
        tokens2 = set(self.preprocess_text(text2))
        score = self.jaccard_similarity(tokens1, tokens2)
        print(f"DEBUG: Calculated similarity score: {score}")
        return score

    def find_matched_sections(self, text1, text2, sentence_similarity_threshold=0.5):
        # Find similar sentences between two texts
        print("DEBUG: Real find_matched_sections called.")
        sentences1 = self.split_into_sentences(text1)
        sentences2 = self.split_into_sentences(text2)
        matched_sections = []

        # Simple sentence-by-sentence comparison (can be improved)
        for sent1 in sentences1:
            sent1_tokens = set(self.preprocess_text(sent1))
            for sent2 in sentences2:
                sent2_tokens = set(self.preprocess_text(sent2))
                # Calculate similarity between sentences
                sim_score = self.jaccard_similarity(sent1_tokens, sent2_tokens)

                if sim_score > sentence_similarity_threshold: # Threshold for sentence similarity
                    matched_sections.append({
                        "source_sentence": sent1,
                        "matched_sentence": sent2,
                        "similarity": sim_score # Optional: include sentence similarity score
                    })
                    # Avoid matching the same sentence multiple times from text2
                    # break # Uncomment if you only want the best match for each sentence in text1

        print(f"DEBUG: Found {len(matched_sections)} matched sections.")
        return matched_sections
