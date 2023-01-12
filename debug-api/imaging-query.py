from pathlib import Path

from dace_query import DaceClass
from dace_query.imaging import ImagingClass

fp_config = Path('../tests/config.ini')
fp_dacerc = None  # Path('../tests/dev.dacerc')

instance = ImagingClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc)
)

fits_file = "sphere/SPHERE-DRS/DRS-1.0/reduced/2018-08-19/SPHERE_IRDIS.2018-08-19T07:03:54.679_H2.fits"
fits_file = "naco/NACO-ISPYDRS/DRS-1.0/reduced/2017-07-13/NACO.2017-07-14T09:30:13.155_gpca.fits"

instance.get_image(
    fits_file=fits_file,
    file_type='HC',
    output_directory='/tmp',
    output_filename='imaging.fits'
)

x = Path('/tmp', 'imaging.fits').exists()

print(x)
