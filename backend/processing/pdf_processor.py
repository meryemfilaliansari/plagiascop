"""
Module pour le traitement des fichiers PDF.

Contient la logique pour extraire le texte d'un fichier PDF.
"""

import PyPDF2
import hashlib
import io # Import io for handling file-like objects

class PDFProcessor:
    """
    Gère l'extraction de texte à partir de fichiers PDF.
    """
    def __init__(self):
        """
        Initialise le processeur PDF.
        """
        pass # Aucune initialisation spécifique nécessaire pour l'instant

    def process_pdf(self, pdf_file):
        """
        Extrait le texte d'un fichier PDF et calcule son hash SHA-256.

        Args:
            pdf_file (FileStorage): L'objet fichier PDF reçu d'une requête Flask.

        Returns:
            tuple[str, str]: Un tuple contenant le texte extrait du PDF
                             et son hash SHA-256. Retourne ("", "") en cas d'erreur.
        """
        text = ""
        file_hash = ""
        try:
            # Lire le contenu binaire du fichier pour le hash
            pdf_file.seek(0) # S'assurer d'être au début du fichier
            pdf_content = pdf_file.read()
            file_hash = hashlib.sha256(pdf_content).hexdigest()

            # Revenir au début pour la lecture avec PyPDF2
            pdf_file.seek(0)
            # Utiliser io.BytesIO pour que PyPDF2 puisse lire l'objet fichier
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

            # Extraire le texte de chaque page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n" # Ajouter un saut de ligne entre les pages

            print(f"DEBUG: Extracted text from PDF (first 100 chars): {text[:100]}...")
            return text, file_hash

        except PyPDF2.errors.PdfReadError:
            print("ERROR: Failed to read PDF file (corrupted or encrypted).")
            return "", ""
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during PDF processing: {e}")
            return "", ""

