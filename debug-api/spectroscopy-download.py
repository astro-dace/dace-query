from pathlib import Path

from dace_query import DaceClass
from dace_query.spectroscopy import SpectroscopyClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = SpectroscopyClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

instance.download_files(['harps/DRS-3.5/reduced/2019-07-05/HARPS.2019-07-06T04:00:00.322.fits'],
                        file_type='s1d',
                        output_filename='r.tar.gz', output_directory='/tmp')

instance.download_files(
    files=['coralie14/DRS-3.8/reduced/2017-08-05/CORALIE.2017-08-06T10:12:09.000.fits'],
    file_type='guidance',
    output_filename='guidance.tar.gz',
    output_directory='/tmp'
)
