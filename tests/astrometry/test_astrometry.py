import pytest

from dace_query import DaceClass
from dace_query.astrometry import AstrometryClass


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'HD000905', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'HD000905'),
    pytest.param('admin_dace_instance', 'HD199065A'),
])
def test_astrometry_get_timeseries(instance, target, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.get_gaia_timeseries(target=target, output_format='dict')
    # Result is not empty
    assert results

    # Check if results are only the expected target
    assert all((target == object_name) for object_name in results['obj_id_catname'])


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'HD6378', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'HD6378'),
    pytest.param('admin_dace_instance', 'Kepler-560'),
])
def test_astrometry_timeseries_keys(instance, target, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.get_gaia_timeseries(target=target, output_format='dict')
    # Result is not empty
    assert results

    expected_keys = [
        'transit_id', 'obj_id_catname', 'gaia_dr2', 'gaia_dr3', 'ccd_number', 'direction_al0_ac1',
        'da_mas_obs_err', 'time_direction_multiplicity', 'tcpsi_obs', 'tspsi_obs', 't_t0', 'cpsi_obs',
        'spsi_obs', 'ppfact_obs', 'da_mas_obs']

    # Check if all parameters are returned
    assert ((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance')
])
def test_astrometry_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # Result is not empty
    assert results
    expected_keys = [
        'transit_id', 'obj_id_catname', 'gaia_dr2', 'gaia_dr3'
    ]

    # Check if all parameters are retruneds
    assert all((key in results.keys()) for key in expected_keys)
