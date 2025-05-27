"""
Module principal de l'application Flask pour PlagiaScope.

Définit les routes web, gère la soumission des documents,
lance les analyses (locale, externe, IA) et affiche les rapports détaillés.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from backend.config import Config
from backend.processing.pdf_processor import PDFProcessor
from backend.processing.text_processor import TextProcessor
from backend.detection.local_comparison import LocalComparator
from backend.detection.external_search import ExternalSearch
from backend.detection.ai_detection import AIDetector
from backend.database.models import Document, ComparisonResult
from backend.database.local_db import get_session
import hashlib
import json

# Initialisation unique des comparateurs et détecteurs
# Ces objets sont créés une fois au démarrage de l'application
# Les seuils de détection IA peuvent être ajustés ici lors de l'initialisation de AIDetector
local_comparator = LocalComparator()
external_searcher = ExternalSearch()
# Exemple avec des seuils ajustés pour AIDetector (rend le verdict "Probablement IA" plus strict)
# ai_detector = AIDetector(ai_threshold=0.95, uncertain_threshold=0.70)
# Pour utiliser les seuils par défaut (0.85 et 0.5), utilisez :
ai_detector = AIDetector()


app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.CACHE_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite la taille des fichiers à 16MB

def allowed_file(filename):
    """
    Vérifie si l'extension du fichier est autorisée (pdf ou txt).

    Args:
        filename (str): Le nom du fichier à vérifier.

    Returns:
        bool: True si l'extension est 'pdf' ou 'txt', False sinon.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'txt']

@app.route('/', methods=['GET'])
def index():
    """
    Route pour la page d'accueil de l'application.

    Affiche le formulaire de soumission de document.
    Passe un contexte vide au template car aucun résultat n'est affiché initialement ici.

    Returns:
        Response: La page HTML rendue du template index.html.
    """
    # Passer un dictionnaire results vide ou par défaut pour éviter l'erreur UndefinedError
    # dans le template index.html si des parties du template y font référence.
    empty_results = {
        'doc_id': None,
        'text': '',
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
    """
    Route pour l'analyse de document.

    Gère la réception du fichier ou du texte soumis via le formulaire.
    Extrait le texte, le sauvegarde dans la base de données locale,
    lance les analyses (locale, externe, IA) et redirige l'utilisateur
    vers la page de rapport détaillée pour le document analysé.

    Redirige vers la page d'accueil si aucun texte n'est soumis ou si une erreur survient.

    Returns:
        Response: Une redirection vers la page de rapport ou la page d'accueil.
    """
    print(f"DEBUG: Received {request.method} request on /analyze")

    # Si c'est une requête GET sans données, rediriger vers l'index
    # (Cela gère les accès directs à /analyze sans soumission de formulaire)
    if request.method == 'GET' and 'file' not in request.files and 'text' not in request.form:
         print("DEBUG: GET request without data, redirecting to index.")
         return redirect(url_for('index'))

    text = ""
    file_hash = ""
    filename = "Sans nom" # Default filename

    # Tenter de traiter le fichier s'il est présent et non vide
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) # Not strictly needed if processing from file object

            try:
                if file.filename.lower().endswith('.pdf'):
                    print(f"DEBUG: Processing PDF file: {filename}")
                    # Le processeur PDF retourne le texte et le hash
                    text, file_hash = PDFProcessor().process_pdf(file) # Créer une nouvelle instance si process_pdf prend un objet fichier
                else: # Assume .txt
                    print(f"DEBUG: Processing text file: {filename}")
                    # Lire le contenu du fichier texte
                    text = file.read().decode('utf-8')
                    # Calculer le hash du texte
                    file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            except Exception as e:
                print(f"ERROR: Error processing file {filename}: {e}")
                text = "" # Ensure text is empty on error


    # Si aucun texte n'a été obtenu du fichier, tenter de le lire depuis le champ texte
    if not text and 'text' in request.form:
        print("DEBUG: Processing text from form.")
        text = request.form['text']
        # Calculer le hash du texte collé
        file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        filename = "Texte collé" # Default filename for pasted text


    print(f"DEBUG: Text obtained (first 100 chars): {text[:100]}...")
    print(f"DEBUG: Text is empty: {not text}")

    # Si après traitement, aucun texte n'est obtenu (ni fichier, ni champ texte), rediriger vers l'index
    if not text:
        print("DEBUG: No text obtained after processing, redirecting to index.")
        # Optionnel: ajouter un message flash pour l'utilisateur
        # flash("Veuillez soumettre du texte ou un fichier pour analyse.")
        return redirect(url_for('index'))

    # Sauvegarder le document dans la base de données locale
    session = get_session()
    doc_id = None
    try:
        # Vérifier si un document avec ce hash existe déjà
        doc = session.query(Document).filter(Document.hash == file_hash).first()
        if not doc:
            print("DEBUG: Document not found in DB, creating new.")
            # Créer un nouveau document si le hash n'existe pas
            doc = Document(
                title=request.form.get('title', filename), # Utilise le titre du formulaire ou le nom du fichier
                content=text,
                author=request.form.get('author', 'Anonyme'),
                hash=file_hash
            )
            session.add(doc)
            session.commit() # Commit pour obtenir l'ID du nouveau document
            print(f"DEBUG: New document created with ID: {doc.id}")
        else:
             print(f"DEBUG: Document found in DB with ID: {doc.id}.")
             # Mettre à jour la date d'accès si le document existe déjà (optionnel)
             # doc.updated_at = datetime.utcnow()
             # session.commit()
        doc_id = doc.id
    except Exception as e:
        print(f"ERROR: Database error during document save/query: {e}")
        session.rollback() # Annuler les changements en cas d'erreur
        # Optionnel: ajouter un message flash pour l'utilisateur
        # flash("Une erreur est survenue lors de l'enregistrement du document.")
        return redirect(url_for('index'))
    finally:
        session.close() # Toujours fermer la session

    # Vérifier que nous avons bien un doc_id avant de continuer
    if doc_id is None:
         print("ERROR: doc_id is None after database operation, redirecting to index.")
         # Optionnel: ajouter un message flash
         # flash("Impossible d'obtenir l'ID du document pour l'analyse.")
         return redirect(url_for('index'))


    # Effectuer les analyses (locale, externe, IA)
    print("DEBUG: Performing analyses...")
    local_results = []
    external_results = []
    ai_analysis = {'overall_verdict': 'Erreur', 'average_score': 0, 'segments': []} # Default value in case of error

    try:
        # Lancer la comparaison locale
        local_results = local_comparator.find_similar_documents(text, doc_id)
        # Lancer la recherche externe
        external_results = external_searcher.search_external_sources(text)
        # Lancer l'analyse IA
        ai_analysis = ai_detector.analyze_text_segments(text)
        print("DEBUG: Analyses completed.")
    except Exception as e:
        print(f"ERROR: Error during analysis: {e}")
        # En cas d'erreur d'analyse (comme Chromedriver ou API SerpApi),
        # on peut choisir de rediriger vers l'index ou de continuer avec les résultats partiels.
        # Pour l'instant, on continue pour afficher les résultats qui ont fonctionné.
        # Si vous voulez rediriger en cas d'erreur d'analyse, décommentez la ligne ci-dessous:
        # return redirect(url_for('index'))


    # Sauvegarder les résultats de comparaison (locales et externes)
    print("DEBUG: Saving comparison results...")
    session = get_session() # Get a new session for saving results
    try:
        # Combiner les résultats locaux et externes
        all_results = local_results + [{
            'url': r['url'],
            'title': r['title'],
            'similarity': r['similarity'],
            'matched_sections': r['matched_sections']
        } for r in external_results]

        # Sauvegarder les résultats dans la base de données
        # Le verdict IA global est sauvegardé avec chaque résultat de comparaison
        local_comparator.save_comparison_results(
            doc_id,
            all_results,
            is_ai_generated=1 if ai_analysis.get('overall_verdict') == "Probablement IA" else (0 if ai_analysis.get('overall_verdict') == "Probablement humain" else 2), # Convert verdict string to int
            session=session
        )
        session.commit() # Commit les changements pour sauvegarder en base
        print("DEBUG: Comparison results saved.")
    except Exception as e:
        print(f"ERROR: Error saving comparison results: {e}")
        session.rollback() # Annuler les changements en cas d'erreur
        # Optionnel: ajouter un message flash
        # flash("Une erreur est survenue lors de la sauvegarde des résultats.")
        # On peut choisir de rediriger vers l'index ou d'afficher le rapport même sans sauvegarde complète.
        # Pour l'instant, on redirige vers l'index en cas d'erreur de sauvegarde.
        return redirect(url_for('index'))
    finally:
        session.close() # Toujours fermer la session


    # Rediriger vers la page de rapport après une analyse et sauvegarde réussies
    report_url = url_for('generate_report', doc_id=doc_id)
    print(f"DEBUG: Analysis complete. Redirecting to report page: {report_url}")
    return redirect(report_url)


@app.route('/report/<int:doc_id>')
def generate_report(doc_id):
    """
    Route pour afficher le rapport d'analyse d'un document spécifique.

    Récupère le document et ses résultats de comparaison associés depuis
    la base de données et les passe au template report.html pour l'affichage.

    Args:
        doc_id (int): L'ID du document pour lequel générer le rapport.

    Returns:
        Response: La page HTML rendue du rapport ou une page d'erreur 404
                  si le document n'est pas trouvé, ou une page d'erreur 500
                  en cas d'erreur de base de données ou de rendu.
    """
    print(f"DEBUG: Accessing report page for doc_id: {doc_id}")
    session = get_session()
    try:
        # Récupérer le document par son ID
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"ERROR: Document with ID {doc_id} not found for report.")
            return "Document non trouvé", 404 # Retourne une erreur 404 si le document n'existe pas

        # Récupérer tous les résultats de comparaison associés à ce document
        comparisons = session.query(ComparisonResult).filter(
            ComparisonResult.doc_id == doc_id
        ).order_by(ComparisonResult.similarity_score.desc()).all() # Trie par score de similarité décroissant

        # Parse the matched_sections JSON string into a Python object for each comparison
        # Cela est nécessaire car matched_sections est stocké en TEXT (JSON string) en base
        for comp in comparisons:
            try:
                # Load the JSON string into a Python list/dict
                comp.matched_sections_parsed = json.loads(comp.matched_sections)
                # --- Messages de débogage pour vérifier le parsing ---
                # print(f"DEBUG: Parsed matched_sections for comp ID {comp.id}: {comp.matched_sections_parsed}")
                # print(f"DEBUG: Type of parsed matched_sections: {type(comp.matched_sections_parsed)}")
                # if isinstance(comp.matched_sections_parsed, list) and comp.matched_sections_parsed:
                #     print(f"DEBUG: Type of first element in parsed list: {type(comp.matched_sections_parsed[0])}")
                #     if isinstance(comp.matched_sections_parsed[0], dict):
                #          print(f"DEBUG: Keys in first dict: {comp.matched_sections_parsed[0].keys()}")
                # --- Fin des messages de débogage ---

            except (json.JSONDecodeError, TypeError) as e:
                # Handle cases where the string is not valid JSON or is None
                print(f"ERROR: Failed to parse matched_sections JSON for comp ID {comp.id}: {e}")
                comp.matched_sections_parsed = [] # Default to empty list on error
            except Exception as e:
                 print(f"ERROR: Unexpected error during matched_sections parsing for comp ID {comp.id}: {e}")
                 comp.matched_sections_parsed = []

        # Prepare data for Chart.js in Python
        # Crée les listes de labels et de données pour le graphique de similarité
        chart_labels = []
        chart_data = []
        for comp in comparisons:
            if comp.compared_doc_id:
                # Label pour les correspondances locales
                chart_labels.append(f"Local #{comp.compared_doc_id}")
            elif comp.compared_url:
                # Label pour les correspondances externes (tronque l'URL si trop longue)
                display_url = comp.compared_url
                if len(display_url) > 50:
                    display_url = display_url[:47] + '...'
                chart_labels.append(display_url)
            else:
                # Cas inattendu
                chart_labels.append("Inconnu")
            # Ajoute le score de similarité (déjà en pourcentage entier)
            chart_data.append(comp.similarity_score)


        print(f"DEBUG: Found {len(comparisons)} comparison results for doc_id {doc_id}.")
        # Rend le template report.html en lui passant les données nécessaires
        return render_template('report.html',
                               document=doc,
                               comparisons=comparisons,
                               chart_labels=chart_labels, # Liste des labels pour le graphique
                               chart_data=chart_data)    # Liste des données pour le graphique
    except Exception as e:
        print(f"ERROR: Database error accessing report for doc_id {doc_id}: {e}")
        # En cas d'erreur lors de l'accès à la base de données ou du rendu du template,
        # retourne une page d'erreur générique avec un code 500.
        return "Erreur lors de l'affichage du rapport", 500
    finally:
        session.close() # Toujours fermer la session de base de données

# Point d'entrée pour l'exécution directe du script (utilisé par main.py)
if __name__ == '__main__':
    # Initialise les répertoires si ce script est exécuté directement
    Config.init_dirs()
    # Démarre l'application Flask en mode débogage
    app.run(debug=True)
