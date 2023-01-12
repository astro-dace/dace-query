from pathlib import Path

import pytest

from dace_query import DaceClass
from dace_query.sun import SunClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_sun_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    expected_keys = ['file_rootpath', 'ins_name', 'obj_date_bjd', 'spectro_ccf_rv_corr', 'spectro_analysis_rhk',
                     'spectro_analysis_diff_extinction', 'spectro_flux_sn50', 'clim_airmass', 'spectro_flux_sn10',
                     'spectro_flux_sn20', 'spectro_flux_sn30', 'date_night', 'spectro_ccf_contrast_corr',
                     'spectro_ccf_contrast_err', 'spectro_ccf_rv_err', 'spectro_flux_sn60', 'spectro_cal_berv',
                     'spectro_ccf_fwhm', 'spectro_analysis_berv_helio_bary', 'spectro_analysis_smw',
                     'spectro_ccf_bispan_err', 'spectro_analysis_smw_err', 'spectro_analysis_rhk_err',
                     'spectro_ccf_fwhm_corr', 'spectro_ccf_fwhm_err', 'spectro_ccf_rv', 'obj_pos_coordinates_hms_dms',
                     'spectro_ccf_contrast', 'spectro_ccf_bispan', 'spectro_drs_qc', 'spectro_flux_sn40', 'texp',
                     'spectro_analysis_qualflag', 'prog_id', 'public']

    results = instance.query_database(limit=10, output_format='dict')

    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance', marks=pytest.mark.skip(reason='Too long to execute'))
])
def test_sun_get_timeseries(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    results = instance.get_timeseries(output_format='dict')

    expected_keys = ['filename', 'instrument', 'date_bjd', 'rv', 'rhk', 'rv_diff_extinction', 'sn_order_50', 'airmass',
                     'contrast',
                     'drs_quality', 'sn_order_40', 'bis_span_err', 'smw', 'obs_quality', 'smw_err', 'rv_err',
                     'sn_order_20', 'fwhm',
                     'coordinates', 'contrast_raw', 'rhk_err', 'bis_span', 'contrast_err', 'sn_order_60', 'rv_raw',
                     'berv',
                     'sn_order_10', 'berv_bary_to_helio', 'fwhm_raw', 'fwhm_err', 'sn_order_30', 'texp', 'date_night',
                     'prog_id',
                     'public']
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance, file, file_type', [
    pytest.param('anon_dace_instance', 'harpn/DRS-2.3.5/reduced/2015-07-30/r.HARPN.2015-07-31T08-23-48.980.fits',
                 's1d'),
    pytest.param('anon_dace_instance', 'harpn/DRS-2.3.5/reduced/2015-08-17/r.HARPN.2015-08-17T12-24-56.750.fits', 's2d')

])
def test_sun_download(instance, file, file_type, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    filters = {
        'file_rootpath': {
            'equal': [
                file
            ]
        }
    }
    output_directory = '/tmp'
    output_filename = 'sun_files.tar.gz'
    instance.download(
        file_type='s1d',
        filters=filters,
        output_directory=output_directory,
        output_filename=output_filename)
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize('instance, files', [
    pytest.param('anon_dace_instance', [
        'harpn/DRS-2.3.5/reduced/2015-08-17/r.HARPN.2015-08-17T12-24-56.750.fits',
        'harpn/DRS-2.3.5/reduced/2015-07-30/r.HARPN.2015-07-31T08-23-48.980.fits'
    ])
])
def test_sun_download_files(instance, files, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)
    output_directory = '/tmp'
    output_filename = 'sun_files.tar.gz'
    instance.download_files(
        file_type='s1d',
        files=files,
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)
