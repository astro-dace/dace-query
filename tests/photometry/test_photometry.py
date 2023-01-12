import pytest
from astropy.coordinates import SkyCoord, Angle

from dace_query import DaceClass
from dace_query.photometry import PhotometryClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance'),
])
def test_photometry_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PhotometryClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # Result is not empty
    assert results
    expected_keys = ['obj_id_catname', 'obj_pos_coordinates_hms_dms', 'ins_name', 'file_rootpath', 'prog_id',
                     'obj_date_bjd', 'pub_ref', 'pub_bibcode', 'status_published', 'obj_id_daceid']

    # Check if all parameters are returned
    assert ((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance, status', [
    pytest.param('anon_dace_instance', True),
])
def test_photometry_query_database_anon_access(instance, status, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PhotometryClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # Result is not empty
    assert results
    # Check if results are published or not
    assert all(is_public is status for is_public in results['status_published'])


@pytest.mark.parametrize('instance, sky_coord, expected_target', [
    pytest.param('admin_dace_instance', None, None,
                 marks=pytest.mark.skip(reason="Private objects have no coordinates set")),
    pytest.param('anon_dace_instance', SkyCoord('06h43m33s', '+28d02m46s', frame='icrs'), 'EPIC202066227')
])
def test_photometry_query_region(instance, sky_coord, expected_target: str, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PhotometryClass(dace_instance=dace_instance)

    angle = Angle('0.045d')
    results = instance.query_region(sky_coord=sky_coord, angle=angle, limit=10, output_format='dict')

    # Result is not empty
    assert results

    # Check the geospatial filter
    assert expected_target.lower() in map(lambda name: name.lower(), results['obj_id_catname'])


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'EPIC202059391'),
    pytest.param('anon_dace_instance', 'Feige 110', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'Feige 110')
])
def test_photometry_get_timeseries(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PhotometryClass(dace_instance=dace_instance)

    results = instance.get_timeseries(target)
    # Result is not empty
    assert results
    expected_keys = ['instrument', 'pubBibcode', 'pubRef', 'objDateRjdVect', 'photomFluxVect', 'photomFluxVectErr']
    retrieved_keys = results[0].keys()
    assert all((key in retrieved_keys) for key in expected_keys)
