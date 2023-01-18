from pathlib import Path

from dace_query import DaceClass
from dace_query.cheops import CheopsClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = CheopsClass(dace_instance=DaceClass(config_path=fp_config, dace_rc_config_path=fp_dacerc))

# .. Catalog
values = instance.query_catalog('stellar')
# print(values)

# .. Expected keys
values = instance.query_database(limit=10)
# print(values.keys())

# .. Publicity
results = instance.query_database(limit=10)
all(is_public is True for is_public in results['status_published'])

# Lightcurve

values = instance.get_lightcurve('GJ 606')

file_keys = [
    'CH_PR100002_TG011301_V0102',
    'CH_PR100002_TG011301_V0102',
    'CH_PR100002_TG011301_V0102']
print(values['file_key'][0:10])
x = all(file_key in values['file_key'] for file_key in file_keys)

# Movie download
instance.download_diagnostic_movie(
    file_key='CH_PR100018_TG027204_V0200',
    output_directory='/tmp',
    output_filename='cheops_movie.mp4'
)
# sky_coord, angle = SkyCoord("22h23m29s", "+32d27m34s", frame='icrs'), Angle('0.045d')
# values = instance.query_region(sky_coord=sky_coord, angle=angle)
# print(values)

results = instance.list_data_product(
    visit_filepath='cheops/outtray/PR10/PR100002_TG016604_V0200/CH_PR100002_TG016604_TU2021-02-12T14-49-28_SCI_RAW_SubArray_V0200.fits'
)

print(results.keys())
