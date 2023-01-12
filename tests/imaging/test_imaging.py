from pathlib import Path

import pytest
from astropy.coordinates import SkyCoord, Angle

from dace_query import DaceClass
from dace_query.imaging import ImagingClass


@pytest.mark.parametrize('instance', [
    'anon_dace_instance'
])
def test_imaging_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ImagingClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')

    expected_keys = ['obj_id_catname', 'obj_pos_coordinates_hms_dms', 'ins_name', 'file_rootpath', 'prog_id',
                     'obj_date_bjd', 'date_night', 'ins_drs_name', 'img_filter', 'img_mode', 'status_published',
                     'obj_id_daceid']
    assert results
    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_imaging_query_database_anon_access(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ImagingClass(dace_instance=dace_instance)

    results = instance.query_database(limit=100, output_format='dict')
    assert results
    assert all(results['status_published'])


@pytest.mark.parametrize('instance, sky_coord, expected_target', [
    pytest.param('anon_dace_instance', SkyCoord('02h12m20s', '-46d48m58s', frame='icrs'), 'HD13724'),
    pytest.param('anon_dace_instance', SkyCoord('13h37m56s', '-41d34m29s'), 'MML36', marks=pytest.mark.xfail),
    # Not public
    pytest.param('admin_dace_instance', SkyCoord('13h37m56s', '-41d34m29s'), 'MML36')

])
def test_imaging_query_region(instance, sky_coord, expected_target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ImagingClass(dace_instance=dace_instance)
    angle = Angle('0.045d')
    results = instance.query_region(sky_coord=sky_coord, angle=angle, output_format='dict')
    assert results
    assert expected_target in results['obj_id_catname']


@pytest.mark.parametrize('instance, fits_file', [
    pytest.param('anon_dace_instance',
                 'sphere/SPHERE-DRS/DRS-1.0/reduced/2018-08-19/SPHERE_IRDIS.2018-08-19T07:03:54.679_H2.fits'),
    pytest.param('anon_dace_instance',
                 'naco/NACO-ISPYDRS/DRS-1.0/reduced/2017-07-13/NACO.2017-07-14T09:30:13.155_gpca.fits',
                 marks=pytest.mark.xfail),  # Not public
    pytest.param('admin_dace_instance',
                 'naco/NACO-ISPYDRS/DRS-1.0/reduced/2017-07-13/NACO.2017-07-14T09:30:13.155_gpca.fits')
])
def test_imaging_get_image(instance, fits_file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ImagingClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = Path(fits_file).name
    instance.get_image(
        fits_file=fits_file,
        file_type='HC',
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize('instance, filepath_filter', [
    pytest.param('anon_dace_instance', 'SPHERE.2016-07-20T08:26:19.6113_eclipse.fits'),
    pytest.param('anon_dace_instance', 'NACO.2017-07-14T09:30:13.155_gpca.fits', marks=pytest.mark.xfail),  # Not public
    pytest.param('admin_dace_instance', 'NACO.2017-07-14T09:30:13.155_gpca.fits'),

])
def test_imaging_download_files(instance, filepath_filter, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ImagingClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = 'imaging.tar.gz'
    filters = {
        'file_rootpath': {
            'contains': [filepath_filter]
        }
    }
    instance.download(
        file_type='ns',
        filters=filters,
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink()
