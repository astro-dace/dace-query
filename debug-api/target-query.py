from pathlib import Path

from dace_query import DaceClass
from dace_query.target import TargetClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = TargetClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

targets = instance.query_database(limit=10)
print(list(targets.keys()))
