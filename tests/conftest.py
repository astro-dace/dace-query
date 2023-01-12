from pathlib import Path

import pytest

from dace_query import DaceClass


@pytest.fixture()
def admin_dace_instance():
    """Admin dace instance"""
    fp_config = Path(Path(__file__).parent, 'config.ini')
    fp_dacerc = Path(Path(__file__).parent, 'dev.dacerc')
    dace_instance = DaceClass(config_path=fp_config, dace_rc_config_path=fp_dacerc)
    return dace_instance


@pytest.fixture()
def anon_dace_instance():
    """Anonymous dace instance"""
    fp_config = Path(Path(__file__).parent, 'config.ini')
    dace_instance = DaceClass(config_path=fp_config)
    return dace_instance
