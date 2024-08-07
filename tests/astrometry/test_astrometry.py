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
    "hip_id, gaia_id",
    [
        pytest.param(None, None, id="No id"),
        pytest.param(1000, None, id="HIP id"),
        pytest.param(None, 2361372542600289664, id="Gaia id"),
        pytest.param(1000, 2361372542600289664, id="Both ids"),
        pytest.param(-1, None, id="Invalid HIP id", marks=pytest.mark.xfail),
        pytest.param(
            None, 379224622734044800, id="Conflicting Gaia id", marks=pytest.mark.xfail
        ),
    ],
)
def test_query_hipparcos_database(anon_dace_instance, hip_id, gaia_id):
    # dace_instance: DaceClass = request.getfixturevalue(instance)
    dace_instance: DaceClass = anon_dace_instance
    instance = AstrometryClass(dace_instance=dace_instance)

    if not hip_id and not gaia_id:
        with pytest.raises(
            ValueError, match="Please provide either a HIP id or a Gaia DR3 id."
        ):
            instance.query_hipparcos_database(
                hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
            )
    elif hip_id and gaia_id:
        with pytest.raises(
            ValueError,
            match="Both a HIP id and a Gaia id were given. Please only provide one.",
        ):
            instance.query_hipparcos_database(
                hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
            )
    else:
        results = instance.query_hipparcos_database(
            hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
        )
        # Result is not empty
        assert results

        # Check if results contain either HIP id or Gaia id
        if hip_id:
            assert results["hip"][0] == hip_id
        elif gaia_id:
            gaia_gaiadr3_id = results["gaia_gaiadr3_id"][0]
            simbad_gaiadr3_id = results["simbad_gaiadr3_id"][0]
            # One of both should be equal to the given Gaia id
            assert str(gaia_id) in [gaia_gaiadr3_id, simbad_gaiadr3_id]
            # But not different if both exist
            if gaia_gaiadr3_id != "None" and simbad_gaiadr3_id != "None":
                assert not (gaia_gaiadr3_id != simbad_gaiadr3_id)


@pytest.mark.parametrize(
    "hip_id, gaia_id",
    [
        pytest.param(None, None, id="No id"),
        pytest.param(1000, None, id="HIP id"),
        pytest.param(None, 2361372542600289664, id="Gaia id"),
        pytest.param(1000, 2361372542600289664, id="Both ids"),
        pytest.param(-1, None, id="Invalid HIP id", marks=pytest.mark.xfail),
        pytest.param(
            None, 379224622734044800, id="Conflicting Gaia id", marks=pytest.mark.xfail
        ),
    ],
)
def test_get_hipparcos_timeseries(anon_dace_instance, hip_id, gaia_id):
    """
    Test the 'get_hipparcos_timeseries' function.

    Parameters:
    - anon_dace_instance: An instance of the DaceClass.
    - hip_id: The Hipparcos ID.
    - gaia_id: The Gaia ID.
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

    if not hip_id and not gaia_id:
        with pytest.raises(
            ValueError, match="Please provide either a HIP id or a Gaia DR3 id."
        ):
            instance.get_hipparcos_timeseries(
                hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
            )
    elif hip_id and gaia_id:
        with pytest.raises(
            ValueError,
            match="Both a HIP id and a Gaia id were given. Please only provide one.",
        ):
            instance.get_hipparcos_timeseries(
                hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
            )

    else:
        results: pd.DataFrame = instance.get_hipparcos_timeseries(
            hip_id=hip_id, gaia_id=gaia_id, output_format="dict"
        )
        # Result is not empty
        assert results
        # Result has expected length
        assert len(results["IORB"]) == 103
        # Check if all columns are present
        assert all((key in results.keys()) for key in expected_keys)
