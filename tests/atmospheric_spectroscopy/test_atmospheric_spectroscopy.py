import pytest

from dace_query import DaceClass
from dace_query.atmosphericSpectroscopy import AtmosphericSpectroscopyClass


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'KELT-9'),
    pytest.param('admin_dace_instance', 'KELT-9')
])
def test_atmospheric_spectroscopy_query(instance, request, target):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtmosphericSpectroscopyClass(dace_instance=dace_instance)
    results = instance.query_database(output_format='dict')
    # Results is not empty
    assert results

    # Check if all parameters are returned
    expected_keys = [
        'obj_id_catname', 'obj_id_name', 'spectral_domains', 'ins_name', 'spectral_transitions', 'pub_bibcode',
        'description', 'prog_id', 'obs_type', 'file_rootpath', 'status_published']
    assert all(key in results.keys() for key in expected_keys)

    # Check the presence of a specified target
    assert target in results['obj_id_catname']
