from pathlib import Path

from dace_query import DaceClass
from dace_query.astrometry import AstrometryClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

astrometry_instance = AstrometryClass(dace_instance=DaceClass(config_path=fp_config, dace_rc_config_path=fp_dacerc))

target_to_search = 'HD000905'
values = astrometry_instance.get_gaia_timeseries(target_to_search)
print(list(values.keys()))

values = astrometry_instance.query_database(limit=10)
print(list(values.keys()))
