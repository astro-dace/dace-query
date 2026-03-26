from pathlib import Path

import numpy as np
import pytest
from astropy.coordinates import Angle, SkyCoord
from astropy.io import fits
from astropy.io.fits import HDUList

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
            marks=pytest.mark.xfail
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
            "NIRPS.2022-11-29T05:06:14.564.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
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
            "NIRPS.2022-11-29T05:06:14.564.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
        ),
    ],
)
def test_spectroscopy_browse_latest_drs(instance, file, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    
    products_df = instance.browse_products(
        filters=filters,
        file_type="S1D_A",
        output_format="pandas"
    )
    
    products_latest_drs_df =  instance.browse_products(
        filters=filters,
        file_type="S1D_A",
        drs_version="latest",
        output_format="pandas"
    )
    
    assert not products_df.empty and not products_latest_drs_df.empty
    
    # Check that we've got a file extension in the results that matches the expected file type
    assert all(product_file_ext == "S1D_A" for product_file_ext in products_df["file_ext"])
    assert all(product_file_ext == "S1D_A" for product_file_ext in products_latest_drs_df["file_ext"])
    
    expected = products_df.sort_values(
        by=['version_major', 'version_minor', 'version_patch'], 
        ascending=False
    ).iloc[0]
    
    expected_major = expected['version_major']
    expected_minor = expected['version_minor']
    expected_patch = expected['version_patch']
    
    actual_major = products_latest_drs_df.iloc[0]['version_major']
    actual_minor = products_latest_drs_df.iloc[0]['version_minor']
    actual_patch = products_latest_drs_df.iloc[0]['version_patch']
    
    assert (expected_major, expected_minor, expected_patch) == (actual_major, actual_minor, actual_patch)
    
@pytest.mark.parametrize(
    "instance, file, expected_major, expected_minor, expected_patch",
    [
        pytest.param(
            "anon_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
            "3", 
            "3", 
            "12",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
            "3", 
            "3", 
            "12",
        ),
    ],
)
def test_spectroscopy_browse_specific_drs(instance, file, expected_major, expected_minor, expected_patch, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance : SpectroscopyClass = SpectroscopyClass(dace_instance=dace_instance)
    filters = {"file_rootname": {"equal": [file]}}
    
    version_str = f"DRS-{expected_major}.{expected_minor}.{expected_patch}"
    
    products_df = instance.browse_products(
        filters=filters,
        file_type="S1D_A",
        drs_version=version_str,
        output_format="pandas"
    )
    
    assert not products_df.empty
    
    # Check that we've got a file extension in the results that matches the expected file type
    assert all(product_file_ext == "S1D_A" for product_file_ext in products_df["file_ext"])
    
    # Extract all DRS versions
    majors = products_df['version_major']
    minors = products_df['version_minor']
    patches = products_df['version_patch']
    
    assert all((expected_major == str(major) for major in majors))
    assert all((expected_minor == str(minor) for minor in minors))
    assert all((expected_patch == str(patch) for patch in patches))


@pytest.mark.parametrize(
    "instance, file",
    [
        pytest.param(
            "anon_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
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
            "NIRPS.2022-11-29T05:06:14.564.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
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
            "NIRPS.2022-11-29T05:06:14.564.fits",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "NIRPS.2022-11-29T05:06:14.564.fits",
        ),
    ],
)
def test_spectroscopy_download_shorthand(instance, file, request):
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
        pytest.param("anon_dace_instance", "HD40307", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance", "HD40307"),
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
        'is_latest_drs',
    ]
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize(
    "instance, target",
    [
        pytest.param("anon_dace_instance", "HD40307", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance", "HD40307"),
    ],
)
def test_spectroscopy_get_timeseries_sorted_by_instrument(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SpectroscopyClass(dace_instance=dace_instance)

    results = instance.get_timeseries(
        target, sorted_by_instrument=True
    )
    # Result is not empty
    assert results

    # Check that we have a dict of dict of dict (instrument -> drs -> instrument_mode)
    first_instrument = list(results.keys())[0]
    first_drs = list(results[first_instrument].keys())[0]
    first_instrument_mode = list(results[first_instrument][first_drs].keys())[0]
    
    # Check that we have the expected structure
    assert isinstance(results, dict)
    assert isinstance(results[first_instrument], dict)
    assert isinstance(results[first_instrument][first_drs], dict)
    assert isinstance(results[first_instrument][first_drs][first_instrument_mode], dict)
    assert "rv" in results[first_instrument][first_drs][first_instrument_mode].keys()
    
    
@pytest.mark.parametrize(
    "instance, target",
    [
        pytest.param("admin_dace_instance", "HD40307"),
    ],
)
def test_spectroscopy_get_timeseries_latest_drs(instance: SpectroscopyClass, target, request):
    instance = SpectroscopyClass(dace_instance=request.getfixturevalue("admin_dace_instance"))
    
    # Only get HARPS03 data for this target
    filters = {
        "instrument_name": {"equal": ["HARPS03"]},
    }
    
    results_latest = instance.get_timeseries(target=target, filters=filters, output_format="pandas", sorted_by_instrument=False, drs_version="latest")
    results_all = instance.get_timeseries(target=target, filters=filters, output_format="pandas", sorted_by_instrument=False)

    assert not results_latest.empty and not results_all.empty
    
    # Sort the results by DRS version and get the latest one from the full results 
    expected = results_all.sort_values(
        by=['version_major', 'version_minor', 'version_patch'], 
        ascending=False
    ).iloc[0]
    
    expected_major = expected['version_major']
    expected_minor = expected['version_minor']
    expected_patch = expected['version_patch']
    
    actual_major = results_latest.iloc[0]['version_major']
    actual_minor = results_latest.iloc[0]['version_minor']
    actual_patch = results_latest.iloc[0]['version_patch']
    
    assert (expected_major, expected_minor, expected_patch) == (actual_major, actual_minor, actual_patch)
    
@pytest.mark.parametrize(
    "instance, target, instrument_version, expected_major, expected_minor, expected_patch",
    [
        pytest.param(
            "anon_dace_instance",
            "HD40307",
            "HARPS03",
            "3", 
            "3", 
            "6",
            marks=pytest.mark.xfail,
        )
    ],
)

def test_spectroscopy_get_timeseries_specific_drs(instance, target, instrument_version, expected_major, expected_minor, expected_patch, request):
    instance = SpectroscopyClass(dace_instance=request.getfixturevalue("admin_dace_instance"))
    
    # Only get HARPS03 data for this target
    filters = {
        "instrument_name": {"equal": [instrument_version]},
    }
    
    results = instance.get_timeseries(target=target, filters=filters, output_format="pandas", sorted_by_instrument=False, drs_version=f"DRS-{expected_major}.{expected_minor}.{expected_patch}")

    assert not results.empty
    
    # Check that all the results have the expected DRS version
    majors = results['version_major']
    minors = results['version_minor']
    patches = results['version_patch']
    
    assert all((expected_major == str(major) for major in majors))
    assert all((expected_minor == str(minor) for minor in minors))
    assert all((expected_patch == str(patch) for patch in patches))
    
@pytest.mark.parametrize(
    "instance, raw_frame_filerootname",
    [
        pytest.param("anon_dace_instance", "HARPS.2015-04-19T23:55:59.061.fits", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance", "HARPS.2015-04-19T23:55:59.061.fits"),
    ],
)
def test_spectroscopy_get_guiding_frame(instance: SpectroscopyClass, raw_frame_filerootname, request):
    instance = SpectroscopyClass(dace_instance=request.getfixturevalue("admin_dace_instance"))
    filters = {"file_rootname": {"contains": [raw_frame_filerootname]}}
    
    raw_frames = instance.query_database(filters=filters, output_format="dict")

    assert raw_frames
    
    # Check that it has a guiding frame using the flag
    has_guiding_frame = raw_frames["has_guiding_frame"][0]
    assert has_guiding_frame
    
    spectrum_id = raw_frames["spectrum_id"][0]
    
    guiding_frame: HDUList = instance.get_guiding_frame(spectrum_id=spectrum_id)
    
    # Check that the guiding frame returned is a valid .fits file
    guiding_frame.verify("exception")
    
    # Check if there is data in primary HDU
    data = guiding_frame[0].data
    
    assert data is not None
    