from pathlib import Path

from dace_query import DaceClass
from dace_query.spectroscopy import SpectroscopyClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = SpectroscopyClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

x = instance.get_timeseries(target='HD215497', sorted_by_instrument=True)
x = instance.query_database(limit=10)
print(x)
