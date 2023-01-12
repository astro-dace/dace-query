from pathlib import Path

from dace_query import DaceClass
from dace_query.photometry import PhotometryClass

fp_config = Path('../tests/config.ini')
fp_dacerc = None  # Path('../tests/dev.dacerc')

instance = PhotometryClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

instance.get_timeseries('EPIC202066227')
instance.get_timeseries('')
