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
    'sphinx_design',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,  # Controls sidebar navigation depth
}

# Remove the sidebar on pages that are not part of the api reference
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/customization.html#hide-the-sidebar
html_sidebars = {
    'dace_introduction' : [],
    'query_options' : [],
    'output_format' : [],
    'usage_examples' : [],
    'changelogs' : [],
}

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

always_document_param_types = False             # avoid duplicate type listings
typehints_format = "short"                      # strip modules from names
typehints_description_target = "documented"


# -- Option for autosectionlabel ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html


# -- exclude_patterns ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns
exclude_patterns = [
    'dace_query.opendata.rst',  # Temporarily exclude this file
    'dace_query.monitoring.rst',  # Temporarily exclude this file
    # These files are temporarily excluded as they do not have functionnal webapps at the moment, they need to be added back to dace_query.rst when functional again
]