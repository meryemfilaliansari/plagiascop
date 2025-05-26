# File: backend/detection/external_search.py
# Remove Selenium imports
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

import time
import random
import hashlib
import json

# Import SerpApi library
from serpapi import GoogleSearch # Assuming google-search-results library is installed

# Assuming SimilarityAnalyzer is available and imported correctly
from backend.detection.similarity_metrics import SimilarityAnalyzer

class ExternalSearch:
    def __init__(self):
        # Remove driver initialization
        # self.driver = None
        self.similarity_analyzer = SimilarityAnalyzer()
        # Store the SerpApi key - Ideally, this should be in a config file or env variable
        self.serpapi_key = "093836651908e694df57e88e2a65f0ba73349c5848550cef06e906bac673b5b1"
        print("DEBUG: ExternalSearch initialized with SerpApi.")
        # Remove driver initialization call
        # self._init_driver()

    # Remove Selenium driver initialization
    # def _init_driver(self):
    #     print("DEBUG: Initializing Chrome driver...")
    #     try:
    #         # ... (Selenium code) ...
    #         print("DEBUG: Chrome driver initialized successfully.")
    #     except Exception as e:
    #         print(f"Erreur d'initialisation du driver: {e}")
    #         raise

    def _perform_search(self, query):
        """Performs a search query using SerpApi."""
        print(f"DEBUG: Performing search for query using SerpApi: {query[:50]}...")

        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google", # Specify the search engine
                "num": 10 # Number of results to fetch (adjust as needed)
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            # Process organic results from SerpApi response
            organic_results = []
            if "organic_results" in results:
                for result in results["organic_results"]:
                    # Extract relevant information from SerpApi result
                    title = result.get("title")
                    url = result.get("link")
                    snippet = result.get("snippet")

                    if url and "google.com" not in url: # Basic check
                         organic_results.append({'title': title, 'url': url, 'snippet': snippet})

            print(f"DEBUG: Found {len(organic_results)} organic search results via SerpApi.")
            return organic_results

        except Exception as e:
            print(f"ERROR: An error occurred during SerpApi search: {e}")
            return []

    def search_external_sources(self, text):
        """Searches external sources (web) for plagiarism using SerpApi."""
        print("DEBUG: Starting external search using SerpApi...")
        # Split text into smaller queries if necessary (e.g., sentences or paragraphs)
        # For simplicity, let's use the first few sentences as a query
        sentences = self.similarity_analyzer.split_into_sentences(text) # Assuming this method exists
        query = " ".join(sentences[:3]) # Use first 3 sentences as query

        if not query:
            print("DEBUG: No text to form a search query.")
            return []

        # Perform the search using SerpApi
        search_results = self._perform_search(query)

        # Process search results to find similarities
        external_matches = []
        # With SerpApi, we get snippets, but not the full page content directly.
        # The current placeholder similarity logic relies on comparing full texts.
        # We will keep the structure but acknowledge the limitation -
        # detailed comparison would require fetching content from each URL,
        # which is a separate step and might still face anti-bot issues on target sites.
        # For now, we'll simulate a match based on the presence of a snippet
        # and use the placeholder similarity/matched_sections.
        for result in search_results:
            try:
                # We have the snippet from SerpApi (result['snippet'])
                # A real implementation would need to fetch the content of result['url']
                # for a proper comparison. This is complex and not covered by SerpApi itself.

                # Placeholder: Simulate finding a match with a random score
                # In a real scenario, you'd compare 'text' with the fetched content of result['url']
                simulated_similarity = random.uniform(0, 0.5) # Simulate low similarity for now
                if simulated_similarity > 0.1: # Example threshold
                     external_matches.append({
                         'url': result['url'],
                         'title': result['title'],
                         'similarity': simulated_similarity,
                         # Matched sections cannot be accurately determined from snippet alone
                         'matched_sections': [] # Placeholder for matched sections
                     })

            except Exception as e:
                print(f"ERROR: An unexpected error occurred processing SerpApi result for {result.get('url', 'N/A')}: {e}")
                continue

        print(f"DEBUG: External search completed using SerpApi. Found {len(external_matches)} potential matches.")
        return external_matches

    # Remove driver quitting
    # def __del__(self):
    #     """Ensures the driver is quit when the object is garbage collected."""
    #     if self.driver:
    #         print("DEBUG: Quitting Chrome driver.")
    #         self.driver.quit()

# Add a placeholder for SimilarityAnalyzer if it's not in a separate file
# In a real project, this would be in backend/detection/similarity_metrics.py
class SimilarityAnalyzer:
    def split_into_sentences(self, text):
        # Simple split by period for placeholder
        return text.split('.')

    def combined_similarity(self, text1, text2):
        # Placeholder similarity calculation
        return 0.0 # Always return 0 for now

    def find_matched_sections(self, text1, text2):
        # Placeholder for finding matched sections
        return [] # Always return empty list for now
