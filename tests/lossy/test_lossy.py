import pytest

from dace_query import DaceClass
from dace_query.lossy import LossyClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_lossy_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = LossyClass(dace_instance=dace_instance)
    results = instance.query_database(limit=5, output_format='dict')
    # Result is not empty
    assert results
    # Check if all parameters are returned
    expected_keys = ['sample_id', 'date', 'experimentalist', 'publication', 'temperature']
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance, sample_id', [
    pytest.param('anon_dace_instance', 'SAMPLE_Charcoal_20160324_000'),
    pytest.param('anon_dace_instance', 'SAMPLE_Olivine_20190329_000', marks=pytest.mark.xfail),  # Not public
    pytest.param('admin_dace_instance', 'SAMPLE_Olivine_20190329_000')
])
def test_lossy_query_database(instance, sample_id, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = LossyClass(dace_instance=dace_instance)

    filters: dict = {
        'sample_id': {
            'equal': [sample_id]
        }
    }
    results = instance.query_database(filters=filters, output_format='dict')
    # Result is not empty
    assert results
    assert all((name == sample_id) for name in results['obj_id_catname'])


@pytest.mark.parametrize('instance, sample_id', [
    pytest.param('anon_dace_instance', 'SAMPLE_SPIPA_Rough_104_20140702_000'),
    pytest.param('anon_dace_instance', 'SAMPLE_SPIPA_C_36_20170927_000', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'SAMPLE_SPIPA_C_36_20170927_000')
])
def test_lossy_get_sample(instance, sample_id, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = LossyClass(dace_instance=dace_instance)

    results = instance.get_sample(sample_id, output_format='dict')
    # Result is not empty
    assert results

    assert all((sample == sample_id) for sample in results['sample_id'])
