from pathlib import Path

import pytest
import requests

from dace_query import DaceClass
from dace_query.sun import SunClass


@pytest.mark.parametrize("instance", [pytest.param("anon_dace_instance")])
def test_sun_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    expected_keys = [
        "file_rootpath",
        "obj_date_bjd",
        "spectro_ccf_rv_corr",
        "spectro_analysis_rhk",
        "spectro_analysis_diff_extinction",
        "spectro_flux_sn50",
        "spectro_flux_sn10",
        "spectro_flux_sn20",
        "spectro_flux_sn30",
        "date_night",
        "spectro_ccf_contrast_corr",
        "spectro_ccf_contrast_err",
        "spectro_ccf_rv_err",
        "spectro_flux_sn60",
        "spectro_cal_berv",
        "spectro_ccf_fwhm",
        "spectro_analysis_berv_helio_bary",
        "spectro_analysis_smw",
        "spectro_ccf_bispan_err",
        "spectro_analysis_smw_err",
        "spectro_analysis_rhk_err",
        "spectro_ccf_fwhm_corr",
        "spectro_ccf_fwhm_err",
        "spectro_ccf_rv",
        "spectro_ccf_contrast",
        "spectro_ccf_bispan",
        "spectro_drs_qc",
        "spectro_flux_sn40",
        "texp",
        "spectro_analysis_qualflag",
        "status_public",
        "ins_name",
        "program_id",
    ]

    results = instance.query_database(limit=10, output_format="dict")

    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize(
    "instance, file, file_type",
    [
        pytest.param(
            "anon_dace_instance",
            "r.HARPN.2018-06-08T13-20-27.252.fits",
            "s1d",
        ),
        pytest.param(
            "anon_dace_instance",
            "r.HARPN.2015-08-17T12-24-56.750.fits",
            "s2d",
        ),
    ],
)
def test_sun_download(instance, file, file_type, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    filters = {"file_rootpath": {"contains": [file]}}
    output_directory = "/tmp"
    output_filename = "sun_files.tar.gz"
    instance.download(
        file_type=file_type,
        filters=filters,
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
            [
                "harpn/DRS-3.0.1/reduced/2016-03-25/r.HARPN.2016-03-25T12-24-21.616.fits",
                "harpn/DRS-3.0.1/reduced/2017-05-03/r.HARPN.2017-05-03T14-01-19.513.fits",
                "harpn/DRS-3.0.1/reduced/2015-08-25/r.HARPN.2015-08-26T08-47-09.360.fits",
            ],
        )
    ],
)
def test_sun_download_files(instance, files, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)
    output_directory = "/tmp"
    output_filename = "sun_files.tar.gz"
    instance.download_files(
        file_type="s1d",
        files=files,
        output_directory=output_directory,
        output_filename=output_filename,
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)


@pytest.mark.parametrize(
    "instance, year",
    [
        pytest.param("anon_dace_instance", "2014"),
        pytest.param("anon_dace_instance", "invalid_year"),
        pytest.param("anon_dace_instance", "2020"),
    ],
)
def test_sun_download_public_release_ccf_invalid_year(instance, year, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    with pytest.raises(ValueError) as excinfo:
        instance.download_public_release_ccf(year=year)

    assert "The only available years are" in str(excinfo.value)


@pytest.mark.parametrize(
    "instance, year, month",
    [
        pytest.param("anon_dace_instance", "2014", "12"),
        pytest.param("anon_dace_instance", "2019", "01"),
        pytest.param("anon_dace_instance", "2016", "13"),
    ],
)
def test_sun_download_public_release_all_invalid_date(instance, year, month, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    with pytest.raises(ValueError) as excinfo:
        instance.download_public_release_all(year=year, month=month)

    if month == "13":
        assert "Year and month must be valid" in str(excinfo.value)
    else:
        assert "The only available dates are between" in str(excinfo.value)


@pytest.mark.parametrize(
    "instance, period",
    [pytest.param("anon_dace_instance", "2016-2017")],
)
def test_sun_download_public_release_timeseries_invalid_period(instance, period, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    with pytest.raises(ValueError) as excinfo:
        instance.download_public_release_timeseries(period=period)

    assert "The only available period is" in str(excinfo.value)


@pytest.mark.parametrize(
    "instance, func_name, args, expected_url_pattern",
    [
        pytest.param(
            "anon_dace_instance",
            "download_public_release_ccf",
            {"year": "2016"},
            "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package_ccf_2016.tar.gz",
        ),
        pytest.param(
            "anon_dace_instance",
            "download_public_release_all",
            {"year": "2016", "month": "07"},
            "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package_s1d_s2d_ccf_2016-07.tar.gz",
        ),
        pytest.param(
            "anon_dace_instance",
            "download_public_release_all",
            {"year": "2016", "month": "7"},
            "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package_s1d_s2d_ccf_2016-07.tar.gz",
        ),
        pytest.param(
            "anon_dace_instance",
            "download_public_release_timeseries",
            {"period": "2015-2018"},
            "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_timeseries_2015-2018.tar.gz",
        ),
    ],
)
def test_sun_public_release_urls_reachable(instance, func_name, args, expected_url_pattern, request: pytest.FixtureRequest, monkeypatch):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = SunClass(dace_instance=dace_instance)

    # Store the URL that would be passed to download_static_file_from_url
    captured_url = None

    def mock_download_static_file_from_url(url, *args, **kwargs):
        nonlocal captured_url
        captured_url = url
        # Don't actually download anything
        return True

    # Patch the download_static_file_from_url method
    monkeypatch.setattr(instance.dace, "download_static_file_from_url", mock_download_static_file_from_url)

    # Call the function being tested with the provided args
    getattr(instance, func_name)(**args)

    # Verify a URL was captured and matches expected pattern
    assert captured_url is not None
    assert captured_url == expected_url_pattern
    
    r = requests.head(captured_url, verify=False)
    assert r.status_code == 200 # Check if the URL is reachable