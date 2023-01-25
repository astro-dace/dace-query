# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
from datetime import date
from pathlib import Path

# Add module to the path
sys.path.insert(0, Path(__file__).parents[2].resolve().as_posix())

# Import version from dace-query
from dace_query.__version__ import __version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dace-query'
copyright = f'{date.today().year}, dace-team'
author = 'dace-team'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Option for autosectionlabel ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html