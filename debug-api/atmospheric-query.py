from pathlib import Path

from dace_query import DaceClass
from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopyClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

astrometry_instance = AtmosphericSpectroscopyClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc)
)

values = astrometry_instance.query_database()
print(values.keys())
assert values
assert 'KELT-9' in values['obj_id_catname']
