import re
from pathlib import Path

from dace_query.cheops import Cheops

# Retrieve cheops visits for the target HD88111
cheops_visits = Cheops.query_database(
    filters={
        'obj_id_catname': {
            'equal': ['HD88111']
        }
    },
    limit=1,
    output_format='dict')

for visit in cheops_visits.get('file_rootpath', []):

    # Get all data products available for the raw file specified (=visit)
    visit_products = Cheops.list_data_product(
        visit_filepath=str(visit),
        output_format='dict'
    )
    # ... check if there are data products
    if (not visit_products) and visit_products.get('file', None):
        continue  # pass loop # log...

    # Get files containing "Attitude" in their name using regex
    files = [product for product in visit_products['file'] if
             re.match('.*attitude.*', Path(product).name, re.IGNORECASE)]
    # ... check if there are files matching the regex
    if not files:
        continue  # pass loop # log...

    # Download the matched files
    Cheops.download_files(
        files=files,
        file_type='files',
        output_directory='/tmp',
        output_filename=f'{Path(visit).parent.name}.tar.gz'
    )
