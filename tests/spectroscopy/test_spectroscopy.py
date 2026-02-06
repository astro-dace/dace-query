from pathlib import Path

import pytest
from astropy.coordinates import Angle, SkyCoord

from dace_query import DaceClass
from dace_query.spectroscopy import SpectroscopyClass


@pytest.mark.parametrize("instance", [pytest.param("anon_dace_instance")])
def test_spectroscopy_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)
    expected_keys = [
        'spectrum_id',
        'target_name',
        'pos',
        'instrument_name',
        'program_name',
        'dpr_catg',
        'dpr_type',
        'obs_start_mjd',
        'file_rootname',
        'date_night',
        'program_code',
        'parallax',
        'target_catname',
        'sp_type',
        'mag_v',
        'mag_i',
        'pm_a',
        'pm_d',
        'ra_deg',
        'dec_deg',
        'has_products_to_display',
        'has_rv',
        'has_guiding_frame',
        ]

    results = instance.query_database(limit=10, output_format="dict")
    # Result is not empty
    assert results
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize("instance, status", [pytest.param("anon_dace_instance", True)])
def test_spectroscopy_query_database_anon_access(instance, status, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format="dict")

    # Result is not empty
    assert results
    assert all(is_public is status for is_public in results["public"])


@pytest.mark.parametrize(
    "instance, sky_coord, expected_target",
    [
        pytest.param(
            "anon_dace_instance",
            SkyCoord("05h54m04s", " -60d01m24s", frame="icrs"),
            "HD 40307",
        ),
        pytest.param(
            "admin_dace_instance",
            SkyCoord("00h20m04s", "-64d52m29s", frame="icrs"),
            "* Zet Tuc",
        ),
    ],
)
def test_spectroscopy_query_region(instance, sky_coord, expected_target: str, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    angle = Angle("0.045d")

    results = instance.query_region(
        sky_coord=sky_coord, angle=angle, limit=10, output_format="dict"
    )
    # Result is not empty
    assert results
    
    target_name_from_coords = results["target_name"][0]
    # Check the geospatial filter
    # Get the first target name from the results and check if it matches the expected target
    assert expected_target.lower() == target_name_from_coords.lower()


@pytest.mark.parametrize(
    "instance, file",
    [
        pytest.param(
            "anon_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
        ),
    ],
)
def test_spectroscopy_browse(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    
    products = instance.browse_products(
        filters=filters,
        file_type="S1D_A"
    )
    
    
    assert products
    
    # Check that we've got a file extension in the results that matches the expected file type
    assert all(product_file_ext == "S1D_A" for product_file_ext in products["file_ext"])

@pytest.mark.parametrize(
    "instance, file",
    [
        pytest.param(
            "anon_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
        ),
    ],
)
def test_spectroscopy_browse_shorthand(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    
    products = instance.browse_products(
        filters=filters,
        file_type="s1d"
    )
    
    
    assert products
    
    # Check that we've got a file extension in the results that matches the expected file type
    assert all((product_file_ext == "S1D_A" or product_file_ext == "S1D_B") for product_file_ext in products["file_ext"])


@pytest.mark.parametrize(
    "instance, file",
    [
        pytest.param(
            "anon_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
        ),
    ],
)
def test_spectroscopy_download(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    output_directory = "/tmp"
    output_filename = "files.tar"
    instance.download(
        filters=filters,
        file_type="S1D_A",
        output_directory=output_directory,
        output_filename=output_filename,
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize(
    "instance, file",
    [
        pytest.param(
            "anon_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS.2016-03-09T02:55:16.776.fits",
        ),
    ],
)
def test_spectroscopy_download_with_shorthand(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    output_directory = "/tmp"
    output_filename = "files.tar"
    instance.download(
        filters=filters,
        file_type="ccf",
        output_directory=output_directory,
        output_filename=output_filename,
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)

@pytest.mark.parametrize(
    "instance, files",
    [
        pytest.param(
            "anon_dace_instance",
            ["harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits"],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            ["harps/DRS-3.5/reduced/2016-03-08/HARPS.2016-03-09T02:55:16.776.fits"],
        ),
    ],
)
def test_spectroscopy_download_files(instance, files, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    output_directory = "/tmp"
    output_filename = "files.tar.gz"
    instance.download_files(
        files=files,
        file_type="s1d",
        output_directory=output_directory,
        output_filename=output_filename,
    )

    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize(
    "instance, target",
    [
        pytest.param("anon_dace_instance", "HD40307"),
        pytest.param("admin_dace_instance", "SW0604-1658"),
    ],
)
def test_spectroscopy_get_timeseries_keys(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.get_timeseries(
        target, sorted_by_instrument=False, output_format="dict"
    )
    # Result is not empty
    assert results

    expected_keys = [
        'rv_id',
        'rjd',
        'ccd_texp',
        'cal_berv',
        'cal_drift_noise',
        'cal_drift_rv',
        'cal_therror',
        'cal_thfile',
        'ccf_asym',
        'ccf_bispan',
        'ccf_bispan_err',
        'ccf_contrast',
        'ccf_contrast_err',
        'ccf_mask',
        'ccf_fwhm',
        'ccf_fwhm_err',
        'ccf_noise',
        'rv',
        'rv_err',
        'ins_mode',
        'drs_qc',
        'thar_lamp_offset_ar',
        'thar_lamp_offset_ar1',
        'thar_lamp_offset_ar2',
        'sn10',
        'sn20',
        'sn30',
        'sn40',
        'sn50',
        'sn60',
        'halpha',
        'halpha_error',
        'halpha_flx_h',
        'halpha_flx_h_error',
        'halpha_flx_r1',
        'halpha_flx_r1_error',
        'halpha_flx_r2',
        'halpha_flx_r2_error',
        'na',
        'na_error',
        'na_flx_d1',
        'na_flx_d1_error',
        'na_flx_d2',
        'na_flx_d2_error',
        'na_flx_r1',
        'na_flx_r1_error',
        'na_flx_r2',
        'na_flx_r2_error',
        'ca',
        'ca_error',
        'ca_flx_k',
        'ca_flx_k_error',
        'ca_flx_h',
        'ca_flx_h_error',
        'ca_flx_r1',
        'ca_flx_r1_error',
        'ca_flx_r2',
        'ca_flx_r2_error',
        'smw',
        'smw_err',
        'rhk',
        'rhk_err',
        'spectrum_id',
        'instrument_group',
        'instrument_id',
        'instrument_name',
        'target_id',
        'target_catname',
        'ra_deg',
        'dec_deg',
        'pos',
        'date_night',
        'dpr_catg',
        'dpr_type',
        'program_id',
        'program_code',
        'pub_reference',
        'pub_bibcode',
        'file_rootname',
        'status_public',
        'drs_id',
        'rv_extraction_method',
        'version_major',
        'version_minor',
        'version_patch',
        'source_product_id',
        'source_product_file_ext',
        'source_product_file_rootname',
        'is_latest_standard_drs',
    ]
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)
