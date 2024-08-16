from pathlib import Path

import pytest

from dace_query import DaceClass
from dace_query.opacity import MoleculeClass


@pytest.mark.parametrize("instance", [pytest.param("anon_dace_instance")])
def test_molecule_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MoleculeClass(dace_instance=dace_instance)

    results = instance.query_database(limit=1, output_format="dict")
    assert results

    expected_keys = [
        "molecule",
        "isotopologue",
        "line_list",
        "pressure_min_exponent_b",
        "wavenumber_max",
        "pressure_max_exponent_b",
        "bin_file_size_mb",
        "dat_file_size_mb",
        "wavenumber_min",
        "temp_max_k",
        "temp_min_k",
        "version",
    ]
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize("instance", [pytest.param("anon_dace_instance")])
def test_molecule_length(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MoleculeClass(dace_instance=dace_instance)

    results = instance.query_database(limit=555, output_format="dict")
    assert results
    total_nb_molecule = 265
    assert total_nb_molecule <= len(results["molecule"])


@pytest.mark.parametrize(
    "instance, isotopologue, line_list, version, temperature, exponent",
    [
        pytest.param("anon_dace_instance", "12C-14N", "MoLLIST", "1.0", "300", "-1.33"),
        pytest.param("anon_dace_instance", "12C-14N", "Yueqi", "1.0", "300", "-1.33"),
        pytest.param(
            "anon_dace_instance",
            "12C-14N",
            "unknown_list",
            "1.0",
            "300",
            "-1.33",
            marks=pytest.mark.xfail,
        ),
        pytest.param("anon_dace_instance", "23Na-2H", "Rivlin", "1.0", "1400", "-2.33"),
    ],
)
def test_molecule_get_data(
    instance, isotopologue, line_list, version, temperature, exponent, request
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MoleculeClass(dace_instance=dace_instance)

    results = instance.get_data(
        isotopologue=isotopologue,
        line_list=line_list,
        version=version,
        temperature=temperature,
        pressure_exponent=exponent,
        output_format="dict",
    )
    # Result is not empty
    assert results
    assert "opacity" in results
    assert len(results["opacity"])


@pytest.mark.parametrize(
    "instance, isotopologue, line_list, version, temperature, exponent, wave_number_boundaries",
    [
        pytest.param(
            "anon_dace_instance", "1H2-16O2", "APTY", "1.0", "50", "-3.66", (10, 30)
        ),
        pytest.param(
            "anon_dace_instance",
            "1H2-16O2",
            "APTY",
            "1.0",
            "50",
            "-3.66",
            (6001, 6005),
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_molecule_get_high_resolution_data(
    instance,
    isotopologue,
    line_list,
    version,
    temperature,
    exponent,
    wave_number_boundaries,
    request,
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MoleculeClass(dace_instance=dace_instance)

    results = instance.get_high_resolution_data(
        isotopologue=isotopologue,
        line_list=line_list,
        version=version,
        temperature=temperature,
        pressure_exponent=exponent,
        wavenumber_boundaries=wave_number_boundaries,
        output_format="dict",
    )
    # Results is not empty
    assert results
    assert "opacity" in results


@pytest.mark.parametrize(
    "instance,isotopologue, line_list, version,temperature_boundaries, pressure_boundaries",
    [
        pytest.param(
            "anon_dace_instance", "13C-18O", "Li2015", "1.0", (50, 100), (2.66, 3)
        ),
        pytest.param(
            "anon_dace_instance",
            "13C-18O",
            "Li2015",
            "1.0",
            (3000, 3200),
            (2.66, 3),
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_molecule_download(
    instance,
    isotopologue,
    line_list,
    version,
    temperature_boundaries,
    pressure_boundaries,
    request,
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MoleculeClass(dace_instance=dace_instance)

    output_directory = "/tmp"
    output_filename = "molecule.tar.gz"

    instance.download(
        isotopologue=isotopologue,
        line_list=line_list,
        version=version,
        temperature_boundaries=temperature_boundaries,
        pressure_boundaries=pressure_boundaries,
        output_directory=output_directory,
        output_filename=output_filename,
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)
