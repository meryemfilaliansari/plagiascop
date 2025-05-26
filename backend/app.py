# File: backend/app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from backend.config import Config
from backend.processing.pdf_processor import PDFProcessor
from backend.processing.text_processor import TextProcessor
from backend.detection.local_comparison import LocalComparator # Assuming save_comparison_results is here now
from backend.detection.external_search import ExternalSearch
from backend.detection.ai_detection import AIDetector # Import AIDetector
from backend.database.models import Document, ComparisonResult
from backend.database.local_db import get_session
import hashlib
import json # Import json for parsing matched_sections

# local_comparator = LocalComparator()  # Initialisation unique - keep this


app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.CACHE_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialiser les composants
pdf_processor = PDFProcessor()
text_processor = TextProcessor()
local_comparator = LocalComparator()
external_searcher = ExternalSearch()
# Initialiser AIDetector avec de nouveaux seuils (exemple : seuil IA plus élevé)
# Vous pouvez ajuster ces valeurs selon la sensibilité souhaitée
ai_detector = AIDetector(ai_threshold=0.95, uncertain_threshold=0.70) # Exemple avec seuils ajustés
# Si vous voulez utiliser les seuils par défaut (0.85 et 0.5), utilisez :
# ai_detector = AIDetector()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'txt']

@app.route('/', methods=['GET'])
def index():
    # Passer un dictionnaire results vide ou par défaut pour éviter l'erreur UndefinedError
    empty_results = {
        'doc_id': None, # Ajouter doc_id pour éviter une erreur potentielle si le template l'utilise
        'text': '', # Ajouter text pour éviter une erreur potentielle si le template l'utilise
        'text_length': 0,
        'local_results': [],
        'external_results': [],
        'ai_analysis': {'overall_verdict': 'N/A', 'average_score': 0, 'segments': []},
        'overall_similarity': 0,
        'processed_at': ''
    }
    print("DEBUG: Rendering index.html with empty results context.")
    return render_template('index.html', results=empty_results)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    print(f"DEBUG: Received {request.method} request on /analyze")

    # Initialiser text et file_hash
    text = ""
    file_hash = ""

    # Tenter de traiter le fichier s'il est présent et non vide
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                if file.filename.lower().endswith('.pdf'):
                    print(f"DEBUG: Processing PDF file: {filename}")
                    text, file_hash = pdf_processor.process_pdf(file)
                else:
                    print(f"DEBUG: Processing text file: {filename}")
                    text = file.read().decode('utf-8')
                    file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest() # Corrected hedigest()
            except Exception as e:
                print(f"ERROR: Error processing file {filename}: {e}")
                text = "" # Ensure text is empty on error

    # Si aucun texte n'a été obtenu du fichier, tenter de le lire depuis le champ texte
    if not text and 'text' in request.form:
        print("DEBUG: Processing text from form.")
        text = request.form['text']
        file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest() # Corrected hedigest()


    print(f"DEBUG: Text obtained (first 100 chars): {text[:100]}...")
    print(f"DEBUG: Text is empty: {not text}")

    # Si après traitement, aucun texte n'est obtenu (ni fichier, ni champ texte), rediriger vers l'index
    if not text:
        print("DEBUG: No text obtained after processing, redirecting to index.")
        return redirect(url_for('index'))

    # Sauvegarder le document dans la base
    session = get_session()
    doc_id = None
    try:
        doc = session.query(Document).filter(Document.hash == file_hash).first()
        if not doc:
            print("DEBUG: Document not found in DB, creating new.")
            doc = Document(
                title=request.form.get('title', 'Sans titre'),
                content=text,
                author=request.form.get('author', 'Anonyme'),
                hash=file_hash
            )
            session.add(doc)
            session.commit()
            print(f"DEBUG: New document created with ID: {doc.id}")
        else:
             print(f"DEBUG: Document found in DB with ID: {doc.id}")
        doc_id = doc.id
    except Exception as e:
        print(f"ERROR: Database error during document save/query: {e}")
        session.rollback()
        return redirect(url_for('index'))
    finally:
        session.close()

    if doc_id is None:
         print("ERROR: doc_id is None after database operation, redirecting to index.")
         return redirect(url_for('index'))


    # Effectuer les analyses
    print("DEBUG: Performing analyses...")
    try:
        local_results = local_comparator.find_similar_documents(text, doc_id)
        external_results = external_searcher.search_external_sources(text)
        ai_analysis = ai_detector.analyze_text_segments(text) # Use the initialized ai_detector
        print("DEBUG: Analyses completed.")
    except Exception as e:
        print(f"ERROR: Error during analysis: {e}")
        # En cas d'erreur d'analyse (comme Chromedriver), rediriger vers l'index
        return redirect(url_for('index'))


    # Sauvegarder les résultats
    print("DEBUG: Saving comparison results...")
    session = get_session() # Get a new session for saving results
    try:
        all_results = local_results + [{
            'url': r['url'],
            'title': r['title'],
            'similarity': r['similarity'],
            'matched_sections': r['matched_sections']
        } for r in external_results]

        # Pass the session to the save_comparison_results method
        local_comparator.save_comparison_results(
            doc_id,
            all_results,
            is_ai_generated=1 if ai_analysis['overall_verdict'] == "Probablement IA" else 0,
            session=session # Pass the session here
        )
        session.commit() # Commit the changes
        print("DEBUG: Comparison results saved.")
    except Exception as e:
        print(f"ERROR: Error saving comparison results: {e}")
        session.rollback() # Rollback in case of error
        return redirect(url_for('index'))
    finally:
        session.close() # Close the session


    # Rediriger vers la page de rapport après une analyse réussie
    report_url = url_for('generate_report', doc_id=doc_id)
    print(f"DEBUG: Analysis complete. Redirecting to report page: {report_url}")
    return redirect(report_url)


@app.route('/report/<int:doc_id>')
def generate_report(doc_id):
    print(f"DEBUG: Accessing report page for doc_id: {doc_id}")
    session = get_session()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"ERROR: Document with ID {doc_id} not found for report.")
            return "Document non trouvé", 404

        comparisons = session.query(ComparisonResult).filter(
            ComparisonResult.doc_id == doc_id
        ).order_by(ComparisonResult.similarity_score.desc()).all()

        # Parse the matched_sections JSON string into a Python object for each comparison
        for comp in comparisons:
            try:
                # Load the JSON string into a Python list/dict
                comp.matched_sections_parsed = json.loads(comp.matched_sections)
                # --- NOUVEAUX MESSAGES DE DEBOGAGE ---
                print(f"DEBUG: Parsed matched_sections for comp ID {comp.id}: {comp.matched_sections_parsed}")
                print(f"DEBUG: Type of parsed matched_sections: {type(comp.matched_sections_parsed)}")
                if isinstance(comp.matched_sections_parsed, list) and comp.matched_sections_parsed:
                    print(f"DEBUG: Type of first element in parsed list: {type(comp.matched_sections_parsed[0])}")
                    if isinstance(comp.matched_sections_parsed[0], dict):
                         print(f"DEBUG: Keys in first dict: {comp.matched_sections_parsed[0].keys()}")
                # --- FIN DES NOUVEAUX MESSAGES DE DEBOGAGE ---

            except (json.JSONDecodeError, TypeError) as e:
                # Handle cases where the string is not valid JSON or is None
                print(f"ERROR: Failed to parse matched_sections JSON for comp ID {comp.id}: {e}")
                comp.matched_sections_parsed = [] # Default to empty list on error
            except Exception as e:
                 print(f"ERROR: Unexpected error during matched_sections parsing for comp ID {comp.id}: {e}")
                 comp.matched_sections_parsed = []

        # Prepare data for Chart.js in Python
        chart_labels = []
        chart_data = []
        for comp in comparisons:
            if comp.compared_doc_id:
                chart_labels.append(f"Local #{comp.compared_doc_id}")
            elif comp.compared_url:
                # Truncate long URLs for display
                display_url = comp.compared_url
                if len(display_url) > 50:
                    display_url = display_url[:47] + '...'
                chart_labels.append(display_url)
            else:
                chart_labels.append("Inconnu") # Should not happen if data is consistent
            chart_data.append(comp.similarity_score)


        print(f"DEBUG: Found {len(comparisons)} comparison results for doc_id {doc_id}.")
        # Pass chart data and labels to the template
        return render_template('report.html',
                               document=doc,
                               comparisons=comparisons,
                               chart_labels=chart_labels, # Pass prepared labels
                               chart_data=chart_data)    # Pass prepared data
    except Exception as e:
        print(f"ERROR: Database error accessing report for doc_id {doc_id}: {e}")
        # Ensure a response is returned in case of exception
        return "Erreur lors de l'affichage du rapport", 500
    finally:
        session.close()

if __name__ == '__main__':
    Config.init_dirs()
    app.run(debug=True)
