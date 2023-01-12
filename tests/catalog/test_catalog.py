import pytest

from dace_query import DaceClass
from dace_query.catalog import CatalogClass


@pytest.mark.parametrize('instance, catalog', [
    pytest.param('anon_dace_instance', 'gaiataskforce', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'gaiataskforce'),
    pytest.param('anon_dace_instance', 'k2'),
    pytest.param('admin_dace_instance', 'k2')
])
def test_catalog_access(instance, request, catalog):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CatalogClass(dace_instance=dace_instance)
    results = instance.query_database(catalog, limit=10, output_format='dict')
    # Results is not empty
    assert results


@pytest.mark.parametrize('instance, catalog, parameters', [
    pytest.param('admin_dace_instance', 'gaiataskforce', ['target', 'dr2_source_id', 'dr3_source_id']),
    pytest.param('admin_dace_instance', 'tess', ['obj_id_tic', 'obj_id_toi', 'obj_id_hip'])
])
def test_catalog_parameters(instance, request, catalog, parameters):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CatalogClass(dace_instance=dace_instance)
    results = instance.query_database(catalog, limit=10, output_format='dict')
    # Results is not empty
    assert results

    # Check if specified parameters are returned
    assert all(key in results.keys() for key in parameters)
