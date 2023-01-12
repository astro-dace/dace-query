# WARNING: This module ask tess in development
# but not really, tess-webapp is configured with production urls
import pytest
from astropy.coordinates import Angle, SkyCoord

from dace_query import DaceClass
from dace_query.tess import TessClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_tess_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # result is not empty
    assert results
    expected_keys = ['file_rootpath', 'dataset_id', 'ins_drs_version', 'obj_date_bjd', 'obj_id_catname', 'obj_mag_tess',
                     'obj_phys_mass_msun', 'obj_phys_mh', 'obj_phys_radius_rsun', 'obj_phys_teff_k',
                     'obj_pos_coordinates_hms_dms', 'obj_pos_pm_ra_maspyr', 'obj_pos_pm_dec_maspyr', 'obj_pos_ra_hms',
                     'obj_pos_dec_dms', 'obj_pos_par_mas']

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize('instance, sky_coord, expected_target', [
    pytest.param('admin_dace_instance', SkyCoord('13h50m24s', '-60d21m11s', frame='icrs'), 'TIC381400181'),
    pytest.param('anon_dace_instance', SkyCoord('17h14m07s', ' -33d29m40s', frame='icrs'), 'TIC150633616')
])
def test_tess_query_region(instance, sky_coord, expected_target: str, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    angle = Angle('0.045d')

    results = instance.query_region(sky_coord=sky_coord, angle=angle, limit=10, output_format='dict')
    # Result is not empty
    assert results
    # Check the geospatial filter
    assert expected_target.lower() in map(lambda name: name.lower(), results['obj_id_catname'])


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'TIC338135000'),
    pytest.param('anon_dace_instance', 'TIC150633616'),
])
def test_tess_get_flux(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.get_flux(target, output_format='dict')
    # Result is not empty
    assert results
    expected_keys = ['data', 'smoothModel', 'modelParams']
    assert all((key in results.keys()) for key in expected_keys)

    expected_data_keys = ['id', 'time', 'flux', 'flux_err', 'raw_flux', 'raw_flux_err', 'corr_flux', 'corr_flux_err',
                          'signal', 'signal_err', 'pos_x', 'pos_y', 'quality', 'dataset_id', 'model']

    assert all((key in results['data'].keys()) for key in expected_data_keys)
