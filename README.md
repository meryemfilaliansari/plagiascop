# PlagiaScope

## Système Avancé de Détection de Plagiat et d'Analyse de Contenu Généré par IA

![PlagiaScope Logo Placeholder](docs/images/logo_placeholder.png) <!-- Si vous avez un logo, mettez son chemin ici -->

## Table des Matières

1.  [Description du Projet](#description-du-projet)
2.  [Fonctionnalités](#fonctionnalités)
3.  [Technologies Utilisées](#technologies-utilisées)
4.  [Configuration et Installation](#configuration-et-installation)
    *   [Prérequis](#prérequis)
    *   [Cloner le Dépôt](#cloner-le-dépôt)
    *   [Environnement Virtuel](#environnement-virtuel)
    *   [Installation des Dépendances](#installation-des-dépendances)
    *   [Exécution du Script de Configuration](#exécution-du-script-de-configuration)
    *   [Configuration de l'API SerpApi](#configuration-de-lapi-serpapi)
    *   [Configuration des Seuils de Détection IA](#configuration-des-seuils-de-détection-ia)
    *   [Vérification de Chromedriver (si nécessaire)](#vérification-de-chromedriver-si-nécessaire)
5.  [Exécution de l'Application](#exécution-de-lapplication)
6.  [Utilisation de l'Interface Web](#utilisation-de-linterface-web)
    *   [Page d'Accueil](#page-daccueil)
    *   [Page de Rapport](#page-de-rapport)
7.  [Structure du Projet](#structure-du-projet)
8.  [Base de Données Locale](#base-de-données-locale)
9.  [Améliorations Possibles](#améliorations-possibles)
10. [Auteurs](#auteurs)
11. [Licence](#licence)

## 1. Description du Projet

PlagiaScope est une application web robuste conçue pour aider les utilisateurs à vérifier l'originalité de leurs documents et à identifier les passages potentiellement générés par intelligence artificielle. Développé en Python avec le framework Flask, il offre une solution complète pour comparer des textes avec une collection de documents locaux et des sources disponibles sur Internet via l'API SerpApi.

L'objectif principal est de fournir un outil simple mais puissant pour les étudiants, les enseignants, les chercheurs ou toute personne ayant besoin d'analyser l'authenticité d'un contenu textuel.

## 2. Fonctionnalités

*   **Soumission Flexible :** Les utilisateurs peuvent facilement télécharger des documents aux formats PDF ou TXT, ou simplement coller leur texte directement dans une zone de texte dédiée sur la page d'accueil.
*   **Analyse de Plagiat Locale :** Le texte soumis est comparé à une base de données interne de documents précédemment analysés et stockés. Cela permet de détecter le plagiat provenant de sources déjà traitées par le système.
*   **Analyse de Plagiat Externe (Web) :** En utilisant l'API SerpApi, l'application effectue des recherches sur le web basées sur des extraits du texte soumis et analyse les résultats pour trouver des similarités avec des sources en ligne.
*   **Détection de Contenu IA :** Intègre un modèle de transformeur pré-entraîné (`roberta-base-openai-detector`) pour évaluer la probabilité que différentes sections du texte aient été générées par un modèle d'IA.
*   **Rapport d'Analyse Détaillé :** Après l'analyse, un rapport complet est généré, présentant un résumé, les scores de similarité globaux et par source, une visualisation graphique des similarités, les détails de chaque correspondance trouvée (locale et externe), et le verdict de détection IA par correspondance.
*   **Visualisation des Sections Correspondantes :** Pour chaque correspondance détectée, l'utilisateur peut visualiser les sections spécifiques du texte soumis qui présentent une similarité avec la source trouvée.
*   **Base de Données Locale Persistante :** Les documents analysés sont stockés localement, créant ainsi une base de connaissances croissante pour les futures comparaisons locales.
*   **Interface Utilisateur Intuitive :** Une interface web claire et réactive construite avec Bootstrap, facilitant la soumission de documents et la consultation des rapports.

## 3. Technologies Utilisées

*   **Backend :**
    *   **Python 3.x :** Langage de programmation principal.
    *   **Flask :** Micro-framework web pour construire l'application.
    *   **SQLAlchemy :** ORM (Object-Relational Mapper) pour interagir avec la base de données SQLite.
    *   **Werkzeug :** Bibliothèque utilitaire pour les applications WSGI (utilisée par Flask).
    *   **Hashlib :** Pour calculer les hashs des documents.
    *   **JSON :** Pour sérialiser/désérialiser les données (notamment les sections correspondantes).
    *   **Datetime :** Pour gérer les timestamps.
*   **Détection et Traitement :**
    *   **NLTK (Natural Language Toolkit) :** Pour le traitement du langage naturel (tokenisation, mots vides, etc.).
    *   **Transformers (Hugging Face) :** Pour charger et utiliser le modèle de détection IA (`roberta-base-openai-detector`).
    *   **PyTorch :** Bibliothèque de calcul tensoriel utilisée par le modèle Transformers.
    *   **SerpApi :** API payante/freemium pour obtenir des résultats de recherche structurés de Google et d'autres moteurs, évitant le scraping direct et les CAPTCHAs.
    *   **Selenium :** Bibliothèque pour l'automatisation de navigateur (utilisée potentiellement pour le scraping de contenu web à partir des URLs obtenues via SerpApi, bien que l'implémentation actuelle se concentre sur l'API).
    *   **PyPDF2 :** Pour l'extraction de texte à partir de fichiers PDF.
    *   **python-magic :** Pour détecter le type de fichier.
    *   **Scikit-learn, NumPy :** Bibliothèques scientifiques (potentiellement utilisées pour des métriques de similarité plus avancées, bien que l'implémentation actuelle utilise NLTK/Jaccard).
*   **Frontend :**
    *   **HTML5 :** Structure des pages web.
    *   **CSS3 :** Stylisation (avec Bootstrap).
    *   **Bootstrap 5.3 :** Framework CSS pour une interface réactive et moderne.
    *   **JavaScript :** Pour l'interactivité côté client (gestion du formulaire, graphiques, modales).
    *   **Chart.js :** Bibliothèque JavaScript pour créer des graphiques interactifs.
*   **Base de Données :**
    *   **SQLite :** Base de données légère et sans serveur, stockée dans un fichier unique (`plagiarism_db.sqlite`).

## 4. Configuration et Installation

Suivez attentivement ces étapes pour configurer et exécuter PlagiaScope sur votre machine locale.

### Prérequis

*   Python 3.6 ou supérieur installé.
*   Pip (gestionnaire de paquets Python) installé.
*   Git installé.
*   Un navigateur web moderne (Chrome est recommandé si vous utilisez Selenium pour le scraping de contenu).
*   Une clé API SerpApi (vous pouvez obtenir une clé d'essai gratuite sur [serpapi.com](https://serpapi.com/)).

### Cloner le Dépôt

Ouvrez votre terminal ou invite de commande et exécutez la commande suivante pour cloner le code source depuis GitHub :

```bash
git clone <https://github.com/meryemfilaliansari/PlagiaScope>
cd plagiarism_detector



Environnement Virtuel
Il est fortement recommandé de créer un environnement virtuel pour isoler les dépendances du projet :

bash


# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel

# Sur Windows:
venv\Scripts\activate

# Sur macOS ou Linux:
source venv/bin/activate

Une fois activé, le nom de l'environnement virtuel (venv) apparaîtra au début de votre ligne de commande.

Installation des Dépendances
Avec l'environnement virtuel activé, installez toutes les bibliothèques Python requises en utilisant pip :

bash


pip install -r requirements.txt
Exécution du Script de Configuration
Exécutez le script setup.py pour télécharger les données NLTK nécessaires (pour le traitement du langage naturel) et initialiser la base de données SQLite :

bash


python setup.py
Ce script affichera des messages indiquant la progression du téléchargement de NLTK et la création de la base de données. Il tentera également de vérifier/installer Chromedriver, bien que son succès dépende de votre configuration Chrome/Selenium.

Configuration de l'API SerpApi
Le projet utilise SerpApi pour la recherche web. Vous devez insérer votre clé API dans le code :

Ouvrez le fichier backend/detection/external_search.py.
Trouvez la ligne suivante dans la méthode __init__ de la classe ExternalSearch :
python


self.serpapi_key = "093836651908e694df57e88e2a65f0ba73349c5848550cef06e906bac673b5b1"
Remplacez "093836651908e694df57e88e2a65f0ba73349c5848550cef06e906bac673b5b1" par votre propre clé API SerpApi.
Sauvegardez le fichier.
Configuration des Seuils de Détection IA
Vous pouvez ajuster la sensibilité de la détection IA en modifiant les seuils dans backend/app.py :

Ouvrez le fichier backend/app.py.
Trouvez la section d'initialisation des composants.
Localisez la ligne où ai_detector est initialisé :
python


ai_detector = AIDetector(ai_threshold=0.95, uncertain_threshold=0.70) # Exemple avec seuils ajustés
Modifiez les valeurs ai_threshold et uncertain_threshold selon la sensibilité souhaitée. Des valeurs plus élevées rendent le verdict "Probablement IA" moins fréquent.
Sauvegardez le fichier.
Vérification de Chromedriver (si nécessaire)
Si vous prévoyez d'utiliser Selenium pour scraper le contenu des pages web (ce qui n'est pas entièrement implémenté dans la version actuelle mais pourrait l'être), ou si vous rencontrez des erreurs liées à Selenium, vous pourriez avoir besoin de configurer Chromedriver manuellement :

Vérifiez la version de votre navigateur Google Chrome.
Téléchargez la version correspondante de Chromedriver depuis https://chromedriver.chromium.org/downloads.
Extrayez le fichier chromedriver.exe (ou chromedriver) dans un dossier de votre choix.
Ouvrez backend/detection/external_search.py.
Trouvez la ligne self.chromedriver_path = r"C:\Users\merye\OneDrive\Bureau\plagiarism_detector\chromedriver.exe" dans la méthode __init__ de ExternalSearch.
Remplacez le chemin par le chemin complet vers votre fichier chromedriver.exe.
Sauvegardez le fichier.
5. Exécution de l'Application
Une fois toutes les étapes de configuration terminées et votre environnement virtuel activé, démarrez l'application Flask en exécutant :

bash


python main.py
Le serveur de développement Flask démarrera. Vous verrez des messages dans votre terminal indiquant les adresses locales où l'application est accessible (généralement http://127.0.0.1:5000/ et une adresse IP locale comme http://192.168.1.137:5000/).

6. Utilisation de l'Interface Web
Ouvrez votre navigateur web et accédez à l'une des adresses fournies par le serveur Flask (par exemple, http://127.0.0.1:5000/).

Page d'Accueil
La page d'accueil (index.html) présente un formulaire simple :

Vous pouvez télécharger un fichier PDF ou TXT en utilisant le champ "Ou téléchargez un fichier...".
Alternativement, vous pouvez coller votre texte directement dans la grande zone de texte "Ou collez votre texte ici".
Vous pouvez optionally fournir un titre et un auteur pour le document.
Cliquez sur le bouton "Lancer l'analyse" pour soumettre votre document.
Après avoir cliqué sur "Lancer l'analyse", l'application traitera votre document, effectuera les comparaisons (locale et externe) et l'analyse IA. Une fois l'analyse terminée, vous serez automatiquement redirigé vers la page de rapport.

Page de Rapport
La page de rapport (report.html) affiche les résultats détaillés de l'analyse pour le document soumis :

Document Analysé : Informations sur le document original (titre, auteur, date).
Statistiques : Nombre total de comparaisons trouvées et la similarité la plus élevée.
Visualisation des Similarités : Un graphique à barres montrant la similarité maximale trouvée dans la base locale et sur le web.
Détails des Correspondances : Une liste déroulante (accordéon) pour chaque source de plagiat potentielle trouvée (documents locaux ou URLs externes).
Pour chaque correspondance, vous verrez la source, le score de similarité, la méthode de détection (locale/externe), la date de détection et le verdict IA pour cette correspondance.
Si des sections correspondantes ont été identifiées, un bouton "Voir les sections similaires" apparaîtra, ouvrant une modale affichant les passages similaires dans le document original et la source.
Boutons d'Action : Boutons pour générer un rapport imprimable et pour lancer une nouvelle analyse (retour à la page d'accueil).
7. Structure du Projet
plagiarism_detector/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Routes Flask, logique principale
│   ├── config.py           # Configuration de l'application
│   ├── database/
│   │   ├── __init__.py
│   │   ├── local_db.py     # Gestion de la session SQLAlchemy
│   │   └── models.py       # Définition des modèles de base de données (Document, ComparisonResult)
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── ai_detection.py # Logique de détection IA
│   │   ├── external_search.py # Logique de recherche externe (SerpApi, Selenium)
│   │   └── local_comparison.py # Logique de comparaison locale et SimilarityAnalyzer
│   └── processing/
│       ├── __init__.py
│       ├── pdf_processor.py # Traitement des fichiers PDF
│       └── text_processor.py # Prétraitement général du texte
├── frontend/
│   ├── static/
│   │   ├── css/            # Fichiers CSS (style.css)
│   │   ├── js/             # Fichiers JavaScript (script.js)
│   │   └── images/         # Images (si utilisées)
│   └── templates/
│       ├── base.html       # Template de base (structure commune)
│       ├── index.html      # Page d'accueil (formulaire)
│       └── report.html     # Page de rapport d'analyse
├── tests/                  # Fichiers de tests (si implémentés)
├── .gitignore              # Fichiers et dossiers à ignorer par Git
├── main.py                 # Point d'entrée pour lancer l'application
├── requirements.txt        # Liste des dépendances Python
├── setup.py                # Script de configuration initiale
└── README.md               # Ce fichier
8. Base de Données Locale
La base de données locale est un fichier SQLite nommé plagiarism_db.sqlite créé à la racine du projet (ou dans le répertoire spécifié par Config.DATA_DIR). Elle contient deux tables principales :

documents : Stocke les informations et le contenu des documents analysés.
comparison_results : Stocke les résultats de chaque comparaison effectuée (score, source, sections correspondantes, verdict IA par correspondance).
Cette base de données est automatiquement créée et gérée par SQLAlchemy via le script setup.py et la logique dans backend/database/.

9. Améliorations Possibles
Amélioration des Algorithmes de Similarité : Remplacer les implémentations basiques de SimilarityAnalyzer par des méthodes plus avancées (TF-IDF, Cosine Similarity, N-grams, Embeddings) pour une détection plus précise.
Scraping de Contenu Web : Implémenter la récupération du contenu complet des URLs obtenues via SerpApi pour une comparaison plus approfondie que les simples snippets.
Surlignage Interactif : Surligner les sections plagiées directement dans le texte original affiché sur la page de rapport.
Gestion des Utilisateurs : Ajouter un système d'authentification et de gestion des utilisateurs pour isoler les documents et les rapports.
Support de Formats de Fichiers Supplémentaires : Ajouter la prise en charge d'autres formats (DOCX, ODT, etc.).
Rapports Exportables : Améliorer la fonctionnalité d'exportation de rapport (par exemple, en PDF structuré).
Interface de Gestion des Documents Locaux : Permettre aux utilisateurs de visualiser, supprimer ou organiser les documents stockés dans la base de données locale.
Amélioration de la Détection IA : Explorer d'autres modèles, ajuster les seuils de manière dynamique, ou fournir plus de détails sur l'analyse IA.
10. Auteurs
FILALI ANSARI MERYEM
OULKIASS SALMA
11. Licence
Ce projet est actuellement sans licence spécifiée. Veuillez ajouter un fichier LICENSE si vous souhaitez définir les termes d'utilisation et de distribution.

