import pytest

from dace_query import DaceClass
from dace_query.target import TargetClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance')
])
def test_target_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TargetClass(dace_instance=dace_instance)

    expected_keys = ['obj_id_basename', 'obj_id_catname', 'obj_pos_coordinates_hms_dms', 'ins_name', 'prog_id',
                     'obj_sptype',
                     'obj_pos_plx_mas', 'obj_pos_pmdec_maspyr', 'obj_pos_pmra_maspyr', 'obj_flux_mag_g',
                     'obj_flux_mag_h',
                     'obj_flux_mag_b', 'obj_id_daceid']

    results = instance.query_database(limit=10, output_format='dict')

    # Results is not empty
    assert results

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)
