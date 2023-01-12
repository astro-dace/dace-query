from __future__ import annotations

from dace_query.__version__ import __py_version__, __pkg_name__, __title__, __version__

print(__title__, __pkg_name__, __py_version__, __version__)

# data: dict[str, list] = Exoplanet.query_database(limit=10, output_format='dict')

# print(data.get('obj_id_catname'))
