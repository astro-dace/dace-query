import pandas as pd
import pytest

from dace_query import DaceClass
from dace_query.astrometry import AstrometryClass


@pytest.mark.parametrize(
    "instance, target",
    [
        pytest.param("anon_dace_instance", "HD000905", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance", "HD000905"),
        pytest.param("admin_dace_instance", "HD199065A"),
    ],
)
def test_astrometry_get_timeseries(instance, target, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.get_gaia_timeseries(target=target, output_format="dict")
    # Result is not empty
    assert results

    # Check if results are only the expected target
    assert all((target == object_name) for object_name in results["obj_id_catname"])


@pytest.mark.parametrize(
    "instance, target",
    [
        pytest.param("anon_dace_instance", "HD6378", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance", "HD6378"),
        pytest.param("admin_dace_instance", "Kepler-560"),
    ],
)
def test_astrometry_timeseries_keys(instance, target, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.get_gaia_timeseries(target=target, output_format="dict")
    # Result is not empty
    assert results

    expected_keys = [
        "transit_id",
        "obj_id_catname",
        "gaia_dr2",
        "gaia_dr3",
        "ccd_number",
        "direction_al0_ac1",
        "da_mas_obs_err",
        "time_direction_multiplicity",
        "tcpsi_obs",
        "tspsi_obs",
        "t_t0",
        "cpsi_obs",
        "spsi_obs",
        "ppfact_obs",
        "da_mas_obs",
    ]

    # Check if all parameters are returned
    assert ((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize(
    "instance",
    [
        pytest.param("anon_dace_instance", marks=pytest.mark.xfail),
        pytest.param("admin_dace_instance"),
    ],
)
def test_astrometry_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AstrometryClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format="dict")
    # Result is not empty
    assert results
    expected_keys = ["transit_id", "obj_id_catname", "gaia_dr2", "gaia_dr3"]

    # Check if all parameters are retruneds
    assert all((key in results.keys()) for key in expected_keys)


###########################
@pytest.mark.parametrize(
    "id",
    [
        pytest.param(None, id="No id", marks=pytest.mark.xfail),
        pytest.param("HIP 1000", id="HIP id"),
        pytest.param("Gaia DR3 2361372542600289664", id="Gaia id"),
        pytest.param("HD 812", id="HD id"),
        pytest.param("Invalid ID", id="Invalid id", marks=pytest.mark.xfail),
    ],
)
def test_query_hipparcos_database(anon_dace_instance, id):
    """
    Test the 'query_hipparcos_database' function.

    Parameters
    ----------
    anon_dace_instance : DaceClass
        An instance of the DaceClass.
    id : str
        The identifier (HIP, Gaia DR3, or HD).
    """
    dace_instance: DaceClass = anon_dace_instance
    instance = AstrometryClass(dace_instance=dace_instance)

    if not id:
        with pytest.raises(
            ValueError, match="Please provide either a HIP id or a Gaia DR3 id."
        ):
            instance.query_hipparcos_database(id=id, output_format="dict")
    else:
        results = instance.query_hipparcos_database(id=id, output_format="dict")
        # Result is not empty
        assert results

        # Check if results contain the correct HIP ID (1000)
        assert results["hip"][0] == 1000


@pytest.mark.parametrize(
    "id",
    [
        pytest.param(None, id="No id", marks=pytest.mark.xfail),
        pytest.param("HIP 1000", id="HIP id"),
        pytest.param("Gaia DR3 2361372542600289664", id="Gaia id"),
        pytest.param("HD 812", id="HD id"),
        pytest.param("Invalid ID", id="Invalid id", marks=pytest.mark.xfail),
    ],
)
def test_get_hipparcos_timeseries(anon_dace_instance, id):
    """
    Test the 'get_hipparcos_timeseries' function.

    Parameters
    ----------
    anon_dace_instance : DaceClass
        An instance of the DaceClass.
    id : str
        The identifier (HIP, Gaia DR3, or HD).
    """
    dace_instance: DaceClass = anon_dace_instance
    instance = AstrometryClass(dace_instance=dace_instance)

    expected_keys = [
        "IORB",
        "EPOCH",
        "PARF",
        "CPSI",
        "SPSI",
        "RES",
        "SRES",
        "HIP",
        "T_BJD",
        "S_MAS",
        "CTH",
        "STH",
    ]

    if not id:
        with pytest.raises(
            ValueError, match="Please provide either a HIP id or a Gaia DR3 id."
        ):
            instance.get_hipparcos_timeseries(id=id, output_format="dict")
    else:
        results: pd.DataFrame = instance.get_hipparcos_timeseries(
            id=id, output_format="dict"
        )
        # Result is not empty
        assert results
        # Result has expected length
        assert len(results["IORB"]) == 103
        # Check if all columns are present
        assert all((key in results.keys()) for key in expected_keys)

        # Check that the correct HIP ID (1000) is retrieved
        assert results["HIP"][0] == 1000
