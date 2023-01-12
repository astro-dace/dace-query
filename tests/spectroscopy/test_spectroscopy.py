from pathlib import Path

import pytest
from astropy.coordinates import SkyCoord, Angle

from dace_query import DaceClass
from dace_query.spectroscopy import SpectroscopyClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_spectroscopy_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)
    expected_keys = ['file_rootpath', 'ins_name', 'obj_date_bjd']

    results = instance.query_database(limit=10, output_format='dict')
    # Result is not empty
    assert results
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance, status', [
    pytest.param('anon_dace_instance', True)
])
def test_spectroscopy_query_database_anon_access(instance, status, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')

    # Result is not empty
    assert results
    assert all(is_public is status for is_public in results['public'])


@pytest.mark.parametrize('instance, sky_coord, expected_target', [
    pytest.param('anon_dace_instance', SkyCoord('03h19m55s', ' -43d04m11s', frame='icrs'), 'HD20794'),
    pytest.param('anon_dace_instance', SkyCoord('00h20m04s', '-64d52m29s', frame='icrs'), 'HD1581',
                 marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', SkyCoord('00h20m04s', '-64d52m29s', frame='icrs'), 'HD1581'),
])
def test_spectroscopy_query_region(instance, sky_coord, expected_target: str, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    angle = Angle('0.045d')

    results = instance.query_region(sky_coord=sky_coord, angle=angle, limit=10, output_format='dict')
    # Result is not empty
    assert results
    # Check the geospatial filter
    assert expected_target.lower() in map(lambda name: name.lower(), results['obj_id_catname'])


@pytest.mark.parametrize('instance, file', [
    pytest.param('anon_dace_instance', 'harps/DRS-3.5/reduced/2005-12-24/HARPS.2005-12-25T02:42:50.100.fits'),
    pytest.param('anon_dace_instance', 'harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits',
                 marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits')
])
def test_spectroscopy_download(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)
    filters = {
        'file_rootpath': {
            'equal': [
                file
            ]
        }}
    output_directory = '/tmp'
    output_filename = 'files.tar.gz'
    instance.download('s1d',
                      filters=filters,
                      output_directory=output_directory,
                      output_filename=output_filename)
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize('instance, files', [
    pytest.param('anon_dace_instance', ['harps/DRS-3.5/reduced/2005-12-24/HARPS.2005-12-25T02:42:50.100.fits']),
    pytest.param('anon_dace_instance', ['harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits'],
                 marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', ['harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits'])
])
def test_spectroscopy_download_files(instance, files, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    output_directory = '/tmp'
    output_filename = 'files.tar.gz'
    instance.download_files(files=files,
                            file_type='s1d',
                            output_directory=output_directory,
                            output_filename=output_filename)

    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize('instance, files', [
    pytest.param('anon_dace_instance', ['coralie14/DRS-3.8/reduced/2017-08-05/CORALIE.2017-08-06T10:12:09.000.fits'])
])
def test_spectroscopy_download_guidance_files(instance, files, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = 'guidance.tar.gz'
    instance.download_files(
        files=files,
        file_type='guidance',
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'HD215497'),
    pytest.param('anon_dace_instance', 'SW0604-1658', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'SW0604-1658')
])
def test_spectroscopy_get_timeseries_keys(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.get_timeseries(target, sorted_by_instrument=False, output_format='dict')
    # Result is not empty
    assert results

    expected_keys = ['texp', 'bispan', 'bispan_err', 'drift_noise', 'rjd', 'cal_therror', 'fwhm', 'fwhm_err', 'rv',
                     'rv_err', 'berv', 'ccf_noise', 'rhk', 'rhk_err', 'contrast', 'contrast_err', 'cal_thfile',
                     'spectroFluxSn50', 'protm08', 'protm08_err', 'caindex', 'caindex_err', 'pub_reference',
                     'pub_bibcode', 'drs_qc', 'haindex', 'haindex_err', 'protn84', 'protn84_err', 'naindex',
                     'naindex_err', 'snca2', 'ins_name', 'mask', 'ins_mode', 'public', 'spectroFluxSn20', 'drs_version',
                     'sindex', 'sindex_err', 'drift_used', 'ccf_asym', 'ccf_asym_err', 'date_night', 'raw_file',
                     'prog_id']
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'GJ3543'),
    pytest.param('admin_dace_instance', 'HD-13263')
])
def test_spectroscopy_get_sorted_timeseries(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.get_timeseries(target, sorted_by_instrument=True, output_format='dict')
    # Result is not empty
    assert results
    assert len(results.keys())
