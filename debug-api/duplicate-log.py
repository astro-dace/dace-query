# Issue: Logs are duplicated
# https://stackoverflow.com/questions/7173033/duplicate-log-output-when-using-python-logging-module
from pathlib import Path

from dace_query.dace import DaceClass
from dace_query.exoplanet import ExoplanetClass

import hashlib, time
# print(dt.now(timezone.utc))


dace = DaceClass(config_path=Path('../tests/config.ini'))
ex_0 = ExoplanetClass(dace_instance=dace)

ex_1 = ExoplanetClass(dace_instance=dace)
ex_2 = ExoplanetClass(dace_instance=dace)
ex_3 = ExoplanetClass(dace_instance=dace)
ex_4 = ExoplanetClass(dace_instance=dace)
ex_4 = ExoplanetClass(dace_instance=dace)
ex_4 = ExoplanetClass(dace_instance=dace)
ex_4 = ExoplanetClass(dace_instance=dace)
ex_4 = ExoplanetClass(dace_instance=dace)

ex_0.query_database(limit=0)
ex_1.query_database(limit=0)
ex_2.query_database(limit=0)
