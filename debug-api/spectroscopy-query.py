from pathlib import Path

from dace_query import DaceClass
from dace_query.spectroscopy import SpectroscopyClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = SpectroscopyClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

x = instance.get_timeseries(target='HD215497', sorted_by_instrument=True, output_format='numpy')
print(x.keys())
"""

sky_coord, angle = SkyCoord("23h13m16s", "+57d10m06s", frame='icrs'), Angle('0.045d')

from dace.spectroscopy import Spectroscopy

filters_to_use = {'file_rootpath': {'contains': ['HARPS.2019-07-06T04:00:00.323.fits']}}
# Spectroscopy.download('s1d', filters=filters_to_use, output_directory='/tmp', output_filename='random.tar.gz')


# Spectroscopy.download_files(['harps/DRS-3.5/reduced/2019-07-05/HARPS.2019-07-06T04:00:00.323.fits'],
#                            file_type='all',
#                            output_filename='r.tar.gz', output_directory='/tmp')

filters = {
    'obj_pos_coordinates_hms_dms':
        {'ra': 343.1, 'dec': -56.0675, 'radius': 0.045}
}
values = Spectroscopy.query_database(filters=filters, limit=10)
print(values)
"""
