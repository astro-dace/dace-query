from pathlib import Path

import pytest
from astropy.coordinates import SkyCoord, Angle

from dace_query import DaceClass
from dace_query.cheops import CheopsClass


@pytest.mark.parametrize('instance, catalog_name', [
    pytest.param('anon_dace_instance', 'planet', marks=pytest.mark.xfail),
    pytest.param('anon_dace_instance', 'stellar', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'planet'),
    pytest.param('admin_dace_instance', 'stellar')
])
def test_cheops_catalog_restricted_access(instance, catalog_name, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)
    results = instance.query_catalog(catalog=catalog_name, limit=10, output_format='dict')

    # Check the cheops restricted access
    assert results


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance'),
    pytest.param('admin_dace_instance')
])
def test_cheops_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')

    expected_keys = ['obj_id_catname', 'obj_pos_coordinates_hms_dms', 'date_mjd_start', 'date_mjd_end', 'obj_mag_v',
                     'pi_name', 'prog_id', 'req_id', 'data_arch_rev', 'file_key', 'file_rootpath',
                     'data_pipe_version', 'data_proc_num', 'db_lc_available', 'obj_mag_cheops',
                     'obj_mag_cheops_err', 'obj_mag_v_err', 'obj_sptype', 'obs_exptime', 'obs_id', 'obs_nexp',
                     'obs_total_exptime', 'pi_uid', 'status_published']

    # Check if all parameters are returned
    for key in expected_keys:
        assert key in results.keys(), f"Expected key '{key}' not found in results"


@pytest.mark.parametrize('instance, status', [
    pytest.param('anon_dace_instance', True)
])
def test_cheops_query_database_anon_access(instance, status, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # Results is not empty
    assert results
    # Check if results are published or not
    assert all(is_public is status for is_public in results['status_published'])


@pytest.mark.parametrize('instance, catalog_name', [
    pytest.param('admin_dace_instance', 'planet'),
    pytest.param('admin_dace_instance', 'unknown_catalog', marks=pytest.mark.xfail)
])
def test_cheops_catalog_access_existence(instance, catalog_name, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)
    results = instance.query_catalog(catalog=catalog_name, limit=10, output_format='dict')

    # Check the cheops restricted access
    assert results


@pytest.mark.parametrize('instance, sky_coord, expected_target', [
    pytest.param('admin_dace_instance', SkyCoord('05h31m27s', '-03d40m38s', frame='icrs'), 'GJ 205'),
    pytest.param('anon_dace_instance', SkyCoord('07h45m18s', '+28d01m34s', frame='icrs'), 'Pollux')
])
def test_cheops_query_region(instance, sky_coord, expected_target: str, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)

    angle = Angle('0.045d')
    results = instance.query_region(sky_coord=sky_coord, angle=angle, limit=10, output_format='dict')

    # Results is not empty
    assert results
    # Check the geospatial filter
    assert expected_target.lower() in map(lambda name: name.lower(), results['obj_id_catname'])


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'CD-345246', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'CD-345246')

])
def test_cheops_get_lightcurve(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)

    results = instance.get_lightcurve(target, output_format='dict')
    # Results is not empty
    assert results


@pytest.mark.parametrize('instance, target, file_key', [
    pytest.param('admin_dace_instance', 'GJ4092', 'CH_PR100018_TG032102_V0300'),
    pytest.param('admin_dace_instance', 'EC 12578-2107', 'CH_PR100002_TG011301_V0300')
])
def test_cheops_lightcurve_contains_file_keys(instance, target, file_key, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)
    filters: dict = {'file_key': {'contains': [file_key]}}
    results = instance.get_lightcurve(target=target, filters=filters, output_format='dict')
    assert file_key in results['file_key']


@pytest.mark.parametrize('instance, file_key', [
    pytest.param('anon_dace_instance', 'CH_PR100018_TG027204_V0200', marks=pytest.mark.xfail),  # 'GJ 15 A' # not public
    pytest.param('anon_dace_instance', 'CH_PR300005_TG000101_V0101', marks=pytest.mark.xfail),  # HD 88111 # not public
    pytest.param('admin_dace_instance', 'CH_PR100018_TG027204_V0200'),  # 'GJ 15 A' # not public

])
def test_cheops_download_movie(instance, file_key, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = 'cheops_movie.mp4'

    instance.download_diagnostic_movie(
        file_key=file_key,
        output_directory=output_directory,
        output_filename=output_filename
    )

    file = Path(output_directory, output_filename)
    assert file.exists()
    
    # Check that it weighs more than 15Kb (Empty archive is 10Kb) 
    size = int(file.stat().st_size)
    assert size > 15 * 1024
    file.unlink(missing_ok=True)


@pytest.mark.parametrize('instance, filepath_root', [
    pytest.param('anon_dace_instance', 'PR150100_TG000101_V0300', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'PR150100_TG000101_V0300')

])
def test_cheops_download_file(instance, filepath_root, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = 'cheops.tar.gz'

    filters: dict = {'file_key':
        {
            'contains': [filepath_root]
        }}
    instance.download(
        file_type='reports',
        filters=filters,
        output_directory=output_directory,
        output_filename=output_filename
    )
    
    file = Path(output_directory, output_filename)
    assert file.exists()
    
    # Check that it weighs more than 15Kb (Empty archive is 10Kb) 
    size = int(file.stat().st_size)
    assert size > 15 * 1024
    
    
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.xfail(reason="The test is expected to fail due because the backend does not support this anymore")
@pytest.mark.parametrize('instance, visit_filepath', [
    pytest.param('anon_dace_instance',
                 'cheops/outtray/PR31/PR310080_TG000301_V0200/CH_PR310080_TG000301_TU2021-02-12T00-16-22_SCI_RAW_SubArray_V0200.fits',
                 marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance',
                 'cheops/outtray/PR30/PR300049_TG000501_V0100/CH_PR300049_TG000501_TU2020-03-13T20-06-20_SCI_RAW_HkCe-SubArray_V0100.fits')
])
def test_cheops_list_data_products(instance, visit_filepath, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)

    results = instance.list_data_product(visit_filepath=visit_filepath, output_format='dict')

    assert results
    assert 'file' in results




@pytest.mark.parametrize('instance, visit_filepath', [
    pytest.param('anon_dace_instance','PR150100_TG000101_V0300',marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance','PR150100_TG000101_V0300')
])
def test_cheops_browse(instance, visit_filepath, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)


    filters: dict = {'directory':
        {
            'contains': [visit_filepath]
        }}
    
    results = instance.browse_products(filters=filters, output_format='dict')

    assert results
    assert 'file' in results


@pytest.mark.parametrize('instance, visit_filepath', [
    pytest.param('anon_dace_instance','PR150100_TG000101_V0300',marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance','PR150100_TG000101_V0300')
])
def test_cheops_browse_incorrect_filters(instance, visit_filepath, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = CheopsClass(dace_instance=dace_instance)


    filters: dict = {'directory':
        {
            'contains': [visit_filepath] # typo in 'contain'
        }}
    
    results = instance.browse_products(filters=filters, output_format='dict')

    assert results
    assert 'file' in results

