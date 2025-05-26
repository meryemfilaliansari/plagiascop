import PyPDF2
from io import BytesIO
import hashlib

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(file_stream):
        """Extrait le texte d'un fichier PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Erreur de lecture PDF: {str(e)}")
    
    @staticmethod
    def process_pdf(file):
        """Traite un fichier PDF et retourne son contenu et hash"""
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Le fichier doit être un PDF")
        
        file_stream = BytesIO(file.read())
        text = PDFProcessor.extract_text_from_pdf(file_stream)
        file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        return text, file_hash