from pathlib import Path

from dace_query import DaceClass
from dace_query.sun import SunClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = SunClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))
x = instance.get_timeseries()

print(list(x.keys()))
