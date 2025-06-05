import pytest

from dace_query import DaceClass
from dace_query.catalog import CatalogClass


@pytest.mark.parametrize('instance, catalog', [
    pytest.param('anon_dace_instance', 'k2-epic', marks=pytest.mark.xfail),
    pytest.param('anon_dace_instance', 'tess', marks=pytest.mark.xfail(raises=NotImplementedError)),
    pytest.param('anon_dace_instance', 'toi', marks=pytest.mark.xfail(raises=NotImplementedError)),
    pytest.param('admin_dace_instance', 'k2-epic'),
    pytest.param('anon_dace_instance', 'cascades'),
    pytest.param('admin_dace_instance', 'cascades')
])
def test_catalog_access(instance, request, catalog):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CatalogClass(dace_instance=dace_instance)
    results = instance.query_database(catalog, limit=10, output_format='dict')
    # Results is not empty
    assert results


@pytest.mark.parametrize('instance, catalog, parameters', [
    pytest.param('admin_dace_instance', 'k2-epic', ['obj_id_epic', 'obj_id_k2', 'obj_id_hip']),
    pytest.param('admin_dace_instance', 'cascades', ['obj_id_hd', 'obj_sptype'])
])
def test_catalog_parameters(instance, request, catalog, parameters):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CatalogClass(dace_instance=dace_instance)
    results = instance.query_database(catalog, limit=10, output_format='dict')
    # Results is not empty
    assert results

    # Check if specified parameters are returned
    assert all(key in results.keys() for key in parameters)
