from pathlib import Path

from dace_query import DaceClass
from dace_query.opendata import OpenDataClass

fp_config = Path('../tests/config.ini')
fp_dacerc = None  # Path('../tests/dev.dacerc')

instance = OpenDataClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

filters = {'main_project_label': {'equal': ['project_dev']}}
results = instance.query_database(filters=filters, output_format='dict')

output_directory = '/tmp'
output_filename = 'README.md'
instance.download(
    dace_data_id='dace-od-20226',
    file_type='readme',
    output_directory=output_directory,
    output_filename=output_filename
)
assert Path(output_directory, output_filename).exists()
