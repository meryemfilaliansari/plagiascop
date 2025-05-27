# Configuration file for the Sphinx documentation builder.
#
# For a full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/stable/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/stable/usage/configuration.html#project-information

project = 'PlagiaScope'
copyright = '2023, FILALI ANSARI MERYEM & OULKIASS SALMA' # Année et auteurs
author = 'FILALI ANSARI MERYEM & OULKIASS SALMA'
release = '1.0' # La version de votre projet

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/stable/usage/configuration.html#general-configuration

# Ajoutez les extensions Sphinx ici
extensions = [
    'sphinx.ext.autodoc',       # Pour extraire la doc des docstrings
    'sphinx.ext.napoleon',      # Pour supporter les docstrings Google/NumPy style
    'myst_parser',              # Pour lire les fichiers Markdown (.md)
    'sphinx_rtd_theme',         # Pour utiliser le thème Read the Docs
    'sphinx.ext.viewcode',      # Pour ajouter des liens vers le code source
    'sphinx.ext.intersphinx',   # Pour lier vers d'autres documentations (ex: Python, Flask)
    # Ajoutez d'autres extensions si nécessaire
]
html_theme = "sphinx_rtd_theme"

# Configurez le parser pour les fichiers source (permet d'utiliser .md)
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Le nom du fichier principal (page d'accueil)
master_doc = 'index'

# Les patterns à ignorer lors de la recherche de fichiers source
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# La langue de la documentation
language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/stable/index.html#options-for-html-output

# Le thème HTML à utiliser
html_theme = 'sphinx_rtd_theme'

# Le chemin vers les fichiers statiques (CSS, JS, images)
html_static_path = ['_static']

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

# Configurez les liens vers d'autres documentations
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/2.3.x/', None), # Adaptez la version de Flask si nécessaire
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None), # Adaptez la version de SQLAlchemy si nécessaire
    # Ajoutez d'autres documentations si vous utilisez d'autres bibliothèques majeures
}

# -- Options for autodoc extension -------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# Indiquez à autodoc où trouver votre code Python
import os
import sys
# Le chemin doit pointer vers le répertoire qui contient le package 'backend'
# Si votre structure est plagiarism_detector/backend/...
# alors le chemin à ajouter est le répertoire parent de 'docs', c'est-à-dire la racine du projet
sys.path.insert(0, os.path.abspath('../'))

# Options par défaut pour autodoc (optionnel)
autodoc_default_options = {
    'members': True,          # Inclut les membres (méthodes, attributs)
    'undoc-members': True,    # Inclut les membres sans docstring (pour voir ce qui manque)
    'show-inheritance': True, # Montre l'héritage des classes
}

# -- Options for napoleon extension ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

# Activez le support des styles Google et NumPy docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False # N'inclut pas __init__ si sa docstring est la même que la classe
napoleon_include_private_members = False # N'inclut pas les membres privés (_méthode)
napoleon_include_special_with_doc = True # Inclut les membres spéciaux (__méthode__) s'ils ont une docstring
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False # Utilise :ivar: au lieu de Variables:
napoleon_use_param = True # Utilise :param: au lieu de Parameters:
napoleon_use_rtype = True # Utilise :rtype: au lieu de Returns:

# -- Options for MyST Parser -------------------------------------------------
# https://myst-parser.readthedocs.io/en/stable/configuration.html

# Configurez MyST si vous utilisez des fichiers Markdown
# myst_enable_extensions = [
#     "amsmath",
#     "colon_fence",
#     "deflist",
#     "dollarmath",
#     "fieldlist",
#     "html_admonition",
#     "html_image",
#     "linkify",
#     "replacements",
#     "smartquotes",
#     "strikethrough",
#     "substitution",
#     "tasklist",
# ]
# myst_url_schemes = ("http", "https", "mailto")
# myst_heading_anchors = 3 # Ajoute des ancres aux titres jusqu'au niveau 3

