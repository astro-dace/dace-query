import logging
import os
from pathlib import Path

import pytest

from dace_query import DaceClass
from astroquery.simbad import Conf as SimbadConf


# Change the simbad timeout for CI environments
# This is a workaraound as astroquery timeouts too quickly in some cases
# this causes all tests using astroquery to fail
@pytest.fixture(scope="session", autouse=True)
def configure_simbad_timeout_for_ci():
    is_ci_environment = os.getenv("GITLAB_CI")

    if is_ci_environment:
        original_timeout = SimbadConf.timeout
        new_timeout = 320 # Increase timeout for CI environments
        SimbadConf.timeout = new_timeout
        print(f"CI environment detected. Increased SIMBAD timeout from {original_timeout}s to {SimbadConf.timeout}s.")
        yield # Let tests run
        SimbadConf.timeout = original_timeout
    else:
        yield # Ensure fixture always yields

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
    fp_dacerc = Path('/path/that/does/not/exist/.dacerc') # workaround, if this is unspecified, it will load the user's .dacerc which might run tests as a auth'd user
    dace_instance = DaceClass(config_path=fp_config, dace_rc_config_path=fp_dacerc)
    return dace_instance
