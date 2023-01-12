import pytest

from dace_query import DaceClass
from dace_query.exoplanet import ExoplanetClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_exoplanets_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ExoplanetClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')

    expected_keys = ['obj_id_catname', 'db_info_name', 'pub_info_detectiontype', 'obj_phys_mass_mjup',
                     'obj_phys_msini_mjup', 'obj_phys_radius_rjup', 'obj_orb_period_day', 'obj_orb_a_au',
                     'obj_orb_omega_deg_errmin', 'obj_orb_ecc', 'sys_nplanets', 'obj_orb_stardistance_pc',
                     'obj_parent_phys_teff_k', 'obj_orb_period_day_errmax', 'obj_phys_mass_mjup_errmax',
                     'obj_orb_omega_deg', 'obj_orb_inc_deg_errmax', 'obj_orb_angdist_arcsec_errmax',
                     'obj_orb_bigomega_deg_errmin', 'obj_parent_phys_radius_rsun', 'obj_orb_bigomega_deg',
                     'obj_parent_phys_mass_msun', 'obj_orb_period_day_errmin', 'obj_parent_phys_feh', 'obj_orb_angdist',
                     'obj_orb_tperi_day', 'obj_phys_radius_rjup_errmax', 'obj_orb_ecc_errmin',
                     'obj_parent_phys_teff_k_errmax', 'obj_parent_phys_feh_errmin', 'obj_orb_inc_deg',
                     'obj_orb_k_mps_errmax', 'obj_orb_k_mps_errmin', 'obj_orb_tperi_day_errmin', 'obj_stellar_magv',
                     'obj_orb_stardistance_pc_errmin', 'obj_phys_msini_mjup_errmin', 'obj_orb_ecc_errmax',
                     'obj_orb_stardistance_pc_errmax', 'obj_phys_msini_mjup_errmax', 'obj_orb_omega_deg_errmax',
                     'pub_info_discovered_year', 'pub_info_reference', 'obj_parent_phys_teff_k_errmin',
                     'obj_orb_a_au_errmax', 'obj_parent_phys_feh_errmax', 'obj_phys_radius_rjup_errmin',
                     'obj_parent_phys_radius_rsun_errmax', 'obj_parent_phys_radius_rsun_errmin',
                     'obj_phys_mass_mjup_errmin', 'obj_pos_alpha_deg', 'obj_parent_phys_mass_msun_errmin',
                     'obj_stellar_rhk', 'obj_orb_k_mps', 'obj_pos_delta_deg', 'obj_orb_tperi_day_errmax',
                     'pub_info_updated', 'obj_orb_bigomega_deg_errmax', 'obj_orb_a_au_errmin',
                     'obj_parent_phys_mass_msun_errmax', 'obj_orb_inc_deg_errmin', 'obj_orb_angdist_arcsec',
                     'obj_orb_angdist_arcsec_errmin', 'obj_parent_age_gyr', 'obj_parent_mv', 'obj_phys_eq_temp_k',
                     'obj_parent_phys_lum_lsun', 'obj_insolation_earthfl', 'pub_ads_link', 'obj_phys_radius_rel_unc',
                     'obj_phys_mass_rel_unc', 'obj_phys_density_gpcm3']

    assert all(key in results.keys() for key in expected_keys)


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'L98-58 c'),
    pytest.param('anon_dace_instance', 'unknown_target', marks=pytest.mark.xfail)
])
def test_exoplanet_query_database_with_filters(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = ExoplanetClass(dace_instance=dace_instance)

    filters: dict = {'obj_id_catname': {'equal': [target]}}
    results = instance.query_database(filters=filters, limit=10, output_format='dict')
    assert results
    assert all((target == obj) for obj in results['obj_id_catname'])
