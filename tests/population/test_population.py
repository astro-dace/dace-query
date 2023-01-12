import pytest

from dace_query import DaceClass
from dace_query.population import PopulationClass


@pytest.mark.parametrize('instance, population_id', [
    pytest.param('anon_dace_instance', 'ng96', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'ng96')
])
def test_population_query_database_keys(instance, population_id, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PopulationClass(dace_instance=dace_instance)

    filters = {'population_id': {'equal': [population_id]}}
    results = instance.query_database(filters=filters, output_format='dict')
    # Result is not empty
    assert results

    expected_keys = ['population_id', 'name', 'description', 'image', 'order']

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize('instance, population_id', [
    pytest.param('anon_dace_instance', 'ng76', marks=pytest.mark.xfail),
    pytest.param('admin_dace_instance', 'ng76')
])
def test_population_get_columns(instance, population_id, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PopulationClass(dace_instance=dace_instance)

    results = instance.get_columns(population_id=population_id, output_format='dict')
    # Result is not empty
    assert results

    expected_key = ['system_id', 'planet_id', 'timestep', 'time_yr', 'core_mass', 'envelope_mass', 'total_mass',
                    'total_lum', 'core_lum', 'core_acc_rate', 'envelope_acc_rate', 'core_radius', 'core_envelope_lum',
                    'core_envelope_pressure', 'core_envelope_temp', 'core_envelope_density', 'total_radius',
                    'surface_lum', 'surface_pressure', 'surface_temp', 'semi_major_axis', 'sound_speed_sq',
                    'gas_disc_mass', 'plan_disc_mass', 'hill_sphere_radius', 'bondi_radius', 'global_dt',
                    'mean_plan_surface_density', 'feeding_zone_width', 'capture_radius', 'mean_distance',
                    'disk_midplane_temp', 'disk_midplane_pressure', 'type_migration', 'plan_ejected_mass',
                    'plan_accreted_mass', 'isolation_mass', 'gas_surface_density', 'feeding_zone_inner_bound',
                    'feeding_zone_outer_bound', 'gap_with', 'planet_dt', 'outer_radius', 'core_density',
                    'gas_accreted_mass', 'gas_evaporated_mass', 'outer_pressure', 'outer_temp', 'inst_core_acc_rate',
                    'core_envelope_entro', 'stellar_lum', 'surface_entro', 'stellar_radius', 'contraction_lumi',
                    'energy_new', 'energy_old', 'kenerg', 'solids_lum', 'plan_ecc', 'plan_inc', 'gamma1_or_core_temp',
                    'impact_acc_rate', 'impact_lumi', 'bloating_lumi', 'eccentricity', 'inclination', 'index_dt',
                    'plan_lost_mass', 'kind_migration', 'status', 'gas_star_acc_rate', 'migration_timescale',
                    'ecc_damping_timescale', 'inc_damping_timescale', 'radiogenic_lumi', 'shock_lumi',
                    'surface_density', 'surface_opac', 'kh_timescale', 'type_phase', 'dt_mode', 'dburn_lumi',
                    'frac_deu', 'ed_num', 'mixing_timescale', 'used_gas_surface_density', 'gas_red_factor',
                    'core_envelope_opac', 'tau23_radius', 'tau23_temp', 'tau23_pressure', 'tau23_lumi', 'tau23_mass',
                    'p1bar_radius', 'p1bar_temp', 'p1bar_depth', 'p1bar_mass', 'transit_radius', 'eddington_pressure',
                    'ram_pressure', 'radiated_energy', 'core_energy', 'acutal_lumi', 'lumi_factor', 'energy_factor',
                    'radiation_pressure', 'max_envelope_acc_rate', 'bondi_envelope_acc_rate', 'over_envelope_acc_rate',
                    'outer_disque_radius', 'intrisic_temp', 'long_node', 'long_peri', 'mean_anom', 'min_distance',
                    'start_distance', 'max_distance', 'ice_frac', 'iron_frac', 'star_depth', 'envelope_thermal_energy',
                    'envelope_grav_energy']

    # Check if all parameters are returned
    assert all(key in results['name'] for key in expected_key)


@pytest.mark.parametrize('instance, population_id, age', [
    pytest.param('admin_dace_instance', 'cd2133', 5000000000),
    pytest.param('admin_dace_instance', 'ng76', 400000),
])
def test_population_get_snapshots(instance, population_id, age, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PopulationClass(dace_instance=dace_instance)

    results = instance.get_snapshots(population_id=population_id, years=age, output_format='dict')
    # Result is not empty
    assert results
    assert all((key in results.keys()) for key in instance.SNAPSHOTS_DEFAULT_COLUMN)


@pytest.mark.parametrize('instance, population_id, system_id, planet_id', [
    pytest.param('admin_dace_instance', 'cd2133', 1, 1),
    pytest.param('admin_dace_instance', 'ng76', 1, 1),
])
def test_population_get_track(instance, population_id, system_id, planet_id, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PopulationClass(dace_instance=dace_instance)

    results = instance.get_track(
        population_id=population_id,
        system_id=system_id,
        planet_id=planet_id,
        output_format='dict'
    )
    # Result is not empty
    assert results
    assert all((key in results.keys()) for key in instance.SIMULATIONS_DEFAULT_COLUMN)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_population_get_snapshots_ages(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = PopulationClass(dace_instance=dace_instance)

    expected_ages = ['100000', '200000', '300000', '400000', '500000', '600000', '700000', '800000', '900000',
                     '1000000', '2000000', '3000000', '4000000', '5000000', '6000000', '7000000', '8000000', '9000000',
                     '10000000', '20000000', '30000000', '40000000', '50000000', '60000000', '70000000', '80000000',
                     '90000000', '100000000', '200000000', '300000000', '400000000', '500000000', '600000000',
                     '700000000', '800000000', '900000000', '1000000000', '2000000000', '3000000000', '4000000000',
                     '5000000000', '6000000000', '7000000000', '8000000000', '9000000000', '10000000000']
    results = instance.get_snapshot_ages()
    # Result is not empty
    assert results
    assert results == expected_ages
