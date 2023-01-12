from pathlib import Path

from dace_query import DaceClass
from dace_query.monitoring import MonitoringClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = MonitoringClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

values = instance.query_transfer_by_target(
    instrument='HARPS',
    pipeline='FULL',
    target='HD 86226'
)
print(list(values.keys()))
