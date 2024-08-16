import pytest

from dace_query import DaceClass
from dace_query.monitoring import MonitoringClass


@pytest.mark.parametrize(
    "instance, instrument, pipeline, night, expected_keys",
    [
        # CORALIE14 - FULL
        pytest.param(
            "anon_dace_instance",
            "CORALIE14",
            "FULL",
            "2022-11-02",
            [
                "lasilla_archive_file_name",
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
            marks=pytest.mark.xfail,
            id="CORALIE14 - FULL - anon",
        ),
        # CORALIE14 - FULL
        pytest.param(
            "admin_dace_instance",
            "CORALIE14",
            "FULL",
            "2022-11-02",
            [
                "lasilla_archive_file_name",
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
            id="CORALIE14 - FULL - admin",
        ),
        # ESPRESSO - TRANSFER
        pytest.param(
            "admin_dace_instance",
            "ESPRESSO",
            "TRANSFER",
            "2022-11-09",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
            id="ESPRESSO - TRANSFER - admin",
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPN",
            "GENEVA",
            "2022-10-31",
            [
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
            id="HARPN - GENEVA - admin",
        ),
    ],
)
def test_monitoring_by_night(
    instance, instrument, pipeline, night, expected_keys, request: pytest.FixtureRequest
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MonitoringClass(dace_instance=dace_instance)

    results = instance.query_transfer_by_night(
        instrument=instrument, pipeline=pipeline, night=night, output_format="dict"
    )
    # Result is not empty
    print(results.keys())
    assert results

    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize(
    "instance, instrument, pipeline, period, expected_keys",
    [
        # ECAM - TRANSFER
        pytest.param(
            "anon_dace_instance",
            "ECAM",
            "TRANSFER",
            ("2022-11-08", "2022-11-09"),
            [
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
            marks=pytest.mark.xfail,
        ),
        # ECAM - TRANSFER
        pytest.param(
            "admin_dace_instance",
            "ECAM",
            "TRANSFER",
            ("2022-11-08", "2022-11-09"),
            [
                "lasilla_archive_file_name",
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
            ],
        ),
        # HARPN - GENEVA
        pytest.param(
            "admin_dace_instance",
            "HARPN",
            "GENEVA",
            ("2022-10-04", "2022-10-06"),
            [
                "observation_type",
                "target",
                "program",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
        ),
    ],
)
def test_monitoring_by_period(
    instance,
    instrument,
    pipeline,
    period,
    expected_keys,
    request: pytest.FixtureRequest,
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MonitoringClass(dace_instance=dace_instance)

    results = instance.query_transfer_by_period(
        instrument=instrument, pipeline=pipeline, period=period, output_format="dict"
    )
    # Result is not empty
    assert results
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize(
    "instance, instrument, pipeline, program, expected_keys",
    [
        pytest.param(
            "anon_dace_instance",
            "ESPRESSO",
            "TRANSFER",
            "110.245W.001",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "ESPRESSO",
            "TRANSFER",
            "110.245W.001",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS",
            "TRANSFER",
            "108.22KV.003",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
        ),
    ],
)
def test_monitoring_by_program(
    instance,
    instrument,
    pipeline,
    program,
    expected_keys,
    request: pytest.FixtureRequest,
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MonitoringClass(dace_instance=dace_instance)
    results = instance.query_transfer_by_program(
        instrument=instrument, pipeline=pipeline, program=program, output_format="dict"
    )
    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize(
    "instance, instrument, pipeline, target, expected_keys",
    [
        pytest.param(
            "anon_dace_instance",
            "HARPS",
            "TRANSFER",
            "CPD-63 1435",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS",
            "TRANSFER",
            "CPD-63 1435",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
            ],
        ),
        pytest.param(
            "admin_dace_instance",
            "HARPS",
            "FULL",
            "HD 86226",
            [
                "observation_type",
                "target",
                "program",
                "eso_archive_file_name",
                "ge_archive_file_name",
                "ge_reduced_file_name",
                "dace_reduced_file_name",
            ],
        ),
    ],
)
def test_monitoring_by_target(
    instance,
    instrument,
    pipeline,
    target,
    expected_keys,
    request: pytest.FixtureRequest,
):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = MonitoringClass(dace_instance=dace_instance)

    results = instance.query_transfer_by_target(
        instrument=instrument, pipeline=pipeline, target=target, output_format="dict"
    )
    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)
