from pathlib import Path

from dace_query.dace import DaceClass
from dace_query.tess import TessClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = TessClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

# targets = instance.query_database(limit=10)
# print(list(targets.keys()))

y = instance.get_flux('TIC381400181')
print(list(y['data'].keys()))
