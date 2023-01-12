from pathlib import Path

from dace_query import DaceClass
from dace_query.catalog import CatalogClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = CatalogClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc)
)

values = instance.query_database('gaiataskforce', limit=10)
print(values)
