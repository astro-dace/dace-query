# WARNING: This module ask tess in development
# but not really, tess-webapp is configured with production urls
import pytest
from astropy.coordinates import Angle, SkyCoord

from dace_query import DaceClass
from dace_query.tess import TessClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_tess_query_database_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.query_database(limit=10, output_format='dict')
    # result is not empty
    assert results
    expected_keys = ['file_rootpath', 'pos', 'dataset_id', 'drs_version', 'bjd', 'tic_key', 'mag_tess',
                     'mass_msun', 'mh', 'radius_rsun', 'teff_k', 'pm_ra_maspyr', 'pm_dec_maspyr',
                     'ra_deg', 'dec_deg']

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)
    
@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_tess_query_tic_catalog_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.query_tic_catalog(limit=10, output_format='dict')
    # result is not empty
    assert results

    expected_keys = ['tic_key', 'pos', 'version', 'hip_key', 'tyc_key', 'ucac_key', 'twomass_key', 'sdss_key', 
                     'allwise_key', 'gaia_key', 'apass_key', 'kic_key', 'obj_type', 'type_src', 'ra_deg', 
                     'dec_deg', 'pos_flag', 'pm_ra', 'pm_ra_err', 'pm_dec', 'pm_dec_err', 'pm_flag', 'plx', 
                     'plx_err', 'par_flag', 'gallong', 'gallat', 'eclong', 'eclat', 'b_mag', 'b_mag_err', 
                     'v_mag', 'v_mag_err', 'u_mag', 'u_mag_err', 'g_mag', 'g_mag_err', 'r_mag', 'r_mag_err', 
                     'i_mag', 'i_mag_err', 'z_mag', 'z_mag_err', 'j_mag', 'j_mag_err', 'h_mag', 'h_mag_err', 
                     'k_mag', 'k_mag_err', 'twom_flag', 'w1_mag', 'w1_mag_err', 'w2_mag', 'w2_mag_err', 
                     'w3_mag', 'w3_mag_err', 'w4_mag', 'w4_mag_err', 'gaia_mag', 'gaia_mag_err', 't_mag', 
                     't_mag_err', 'tess_flag', 'spf_flag', 'teff', 'teff_err', 'logg', 'logg_err', 'mh', 
                     'mh_err', 'rad', 'rad_err', 'mass', 'mass_err', 'rho', 'rho_err', 'lumclass', 'lum', 
                     'lum_err', 'd', 'dist_err', 'ebv', 'ebv_err', 'numcont', 'contratio', 'disposition', 
                     'duplicate_id', 'priority', 'eneg_ebv', 'epos_ebv', 'ebv_flag', 'eneg_mass', 'epos_mass', 
                     'eneg_rad', 'epos_rad', 'eneg_rho', 'epos_rho', 'eneg_logg', 'epos_logg', 'eneg_lum', 
                     'epos_lum', 'eneg_dist', 'epos_dist', 'eneg_teff', 'epos_teff', 'teff_flag', 'gaiabp', 
                     'gaiabp_err', 'gaiarp', 'gaiarp_err', 'gaiaqflag', 'v_mag_flag', 'b_mag_flag', 'splists', 
                     'ra_err', 'dec_err', 'ra_orig', 'dec_orig', 'ra_orig_err', 'dec_orig_err', 'raddflag', 
                     'wdflag', 'obj_id', 'lc_available']

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)

@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_tess_query_toi_catalog_keys(instance, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.query_toi_catalog(limit=10, output_format='dict')
    # result is not empty
    assert results
    
    expected_keys = ['tic_key', 'toi_key', 'toi_complete_key', 'pos', 'disp_tess',
                     'disp_tfopwg', 'mag_t', 'mag_t_err', 'source', 'pmra_maspyr',
                     'pmra_maspyr_err', 'pmdec_maspyr', 'pmdec_maspyr_err', 'epoch_bjd',
                     'epoch_bjd_err', 'trans_period_days', 'trans_period_days_err',
                     'trans_duration_hours', 'trans_duration_hours_err', 'trans_depth_mmag',
                     'trans_depth_mmag_err', 'trans_depth_ppm', 'trans_depth_ppm_err',
                     'planet_radius_rearth', 'planet_radius_rearth_err', 'planet_insol_earthflux',
                     'planet_temp', 'detection_snr', 'dist_pc', 'dist_pc_err', 'teff_k',
                     'teff_k_err', 'logg', 'logg_err', 'radius_rsun', 'radius_rsun_err',
                     'mh', 'mh_err', 'sectors', 'comment', 'created', 'updated', 'modified',
                     'ra_deg', 'dec_deg', 'semi_major_axis', 'pm_rocky_mearth', 'pm_volatile_mearth',
                     'pk_rocky_mps', 'pk_volatile_mps', 'lum_lsun', 'pl_insolation', 'twomass_key',
                     'gaia_key', 'kic_key', 'plx', 'plx_err', 'eclong', 'eclat', 'b_mag', 'b_mag_err',
                     'v_mag', 'v_mag_err', 'j_mag', 'j_mag_err', 'h_mag', 'h_mag_err', 'k_mag', 'k_mag_err',
                     'gaia_mag', 'gaia_mag_err', 'mass', 'mass_err', 'rho', 'rho_err', 'lumclass', 'lum',
                     'lum_err', 'ebv', 'ebv_err', 'numcont', 'contratio', 'priority', 'gaiabp', 'gaiabp_err',
                     'gaiarp', 'gaiarp_err', 'rv_available', 'lc_available']

    # Check if all parameters are returned
    assert all(key in results.keys() for key in expected_keys)

@pytest.mark.parametrize('instance, sky_coord, expected_target, catalog', [
    pytest.param('admin_dace_instance', SkyCoord('2h13m49s', '-80d34m58s', frame='icrs'), '270341214', None),
    pytest.param('anon_dace_instance', SkyCoord('2h13m49s', '-80d34m58s', frame='icrs'), '270341214', None),
    pytest.param('admin_dace_instance', SkyCoord('2h13m49s', '-80d34m58s', frame='icrs'), '270341214', "TIC"),
    pytest.param('admin_dace_instance', SkyCoord('2h13m49s', '-80d34m58s', frame='icrs'), '270341214', "TOI"),
])
def test_tess_query_region(instance, sky_coord, expected_target: str, catalog: str, request: pytest.FixtureRequest):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    angle = Angle('0.045d')

    results = instance.query_region(sky_coord=sky_coord, angle=angle, limit=10, output_format='dict', catalog=catalog)

    # Result is not empty
    assert results
    # Check the geospatial filter
    assert expected_target.lower() in map(lambda name: name.lower(), results['tic_key'])


@pytest.mark.parametrize('instance, target', [
    pytest.param('anon_dace_instance', 'TIC270341214'),
    pytest.param('anon_dace_instance', 'TOI173'),
])
def test_tess_get_flux(instance, target, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = TessClass(dace_instance=dace_instance)

    results = instance.get_flux(target, output_format='dict')
    # Result is not empty
    assert results
    expected_keys = ['data', 'smoothModel', 'modelParams']
    assert all((key in results.keys()) for key in expected_keys)

    expected_data_keys = ['id', 'time', 'flux', 'flux_err', 'raw_flux', 'raw_flux_err', 'corr_flux', 'corr_flux_err',
                          'signal', 'signal_err', 'pos_x', 'pos_y', 'quality', 'dataset_id', 'model']

    assert all((key in results['data'].keys()) for key in expected_data_keys)
