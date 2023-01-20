import re
from pathlib import Path

from dace_query import DaceClass
from dace_query.cheops import CheopsClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = CheopsClass(dace_instance=DaceClass(config_path=fp_config, dace_rc_config_path=fp_dacerc))

cheops_visits = instance.query_database(limit=1, output_format='dict')

for visit in cheops_visits.get('file_rootpath', []):

    # List all the data product available for the raw file specified
    visit_products = instance.list_data_product(
        visit_filepath=str(visit),
        output_format='dict'
    )

    # ... check if data products are available
    if (not visit_products) and visit_products.get('file', None):
        continue  # pass loop

    # Get files containing HkCe- in their name
    files = [product for product in visit_products['file'] if re.match('.*HkCe-.*', Path(product).name)]
    print(files)

    # ... check if there are files matching the regexp
    if not files:
        continue  # pass loop

    # Download the specific files
    instance.download_files(
        files=files,
        file_type='files',
        output_directory='/tmp',
        output_filename=f'{Path(visit).parent.name}.tar.gz'
    )
