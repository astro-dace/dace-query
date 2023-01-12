from pathlib import Path

import pytest

from dace_query import DaceClass
from dace_query.opacity import AtomClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_atom_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtomClass(dace_instance=dace_instance)

    expected_keys = ['atom', 'atom_name', 'charge', 'line_list', 'wavenumber_max', 'temp_min_k',
                     'pressure_max_exponent_b', 'pressure_min_exponent_b', 'temp_max_k', 'wavenumber_min',
                     'bin_file_size_mb', 'dat_file_size_mb', 'version', 'atomic_number']

    results = instance.query_database(limit=5, output_format='dict')
    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_atom_length(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtomClass(dace_instance=dace_instance)

    results = instance.query_database(limit=555, output_format='dict')
    assert results
    total_nb_atoms = 552
    assert total_nb_atoms == len(results['atom'])


@pytest.mark.parametrize('instance, atom, charge, line_list, version, temperature, exponent', [
    pytest.param('anon_dace_instance', 'Lu', '0', 'Kurucz', '1.0', '2500', '-8'),
    pytest.param('anon_dace_instance', 'Lu', '0', 'NIST', '1.0', '2500', '-8'),
    pytest.param('anon_dace_instance', 'Lu', '0', 'unknown_line_list', '1.0', '2500', '-8', marks=pytest.mark.xfail),
    pytest.param('anon_dace_instance', 'V', '1', 'VALD', '1.0', '2500', '-8'),

])
def test_atom_get_data(instance, atom, charge, line_list, version, temperature, exponent, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtomClass(dace_instance=dace_instance)

    results = instance.get_data(
        atom=atom,
        charge=charge,
        line_list=line_list,
        version=version,
        temperature=temperature,
        pressure_exponent=exponent,
        output_format='dict'
    )
    # Result is not empty
    assert results
    assert 'opacity' in results
    assert len(results['opacity'])


@pytest.mark.parametrize('instance, atom, charge, line_list, version,temperature, exponent,wave_number_boundaries', [
    pytest.param('anon_dace_instance', 'Lu', '0', 'Kurucz', '1.0', '2500', '-8', (1.01, 3.02)),
    pytest.param('anon_dace_instance', 'Lu', '0', 'Kurucz', '1.0', '2500', '-8', (60000.0, 60001.0),
                 marks=pytest.mark.xfail)  # Max wave numer reached
])
def test_atom_get_high_resolution_data(instance,
                                       atom, charge, line_list, version,
                                       temperature, exponent,
                                       wave_number_boundaries,
                                       request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtomClass(dace_instance)
    results = instance.get_high_resolution_data(
        atom=atom, charge=charge, line_list=line_list, version=version,
        temperature=temperature, pressure_exponent=exponent,
        wavenumber_boundaries=wave_number_boundaries,
        output_format='dict'
    )
    assert results
    assert 'opacity' in results


@pytest.mark.parametrize('instance, atom, charge, line_list, version, temperature_boundaries, pressure_boundaries', [
    pytest.param('anon_dace_instance', 'H', '0', 'Kurucz', '1.0', (2500, 2700), (-8, -8)),
    pytest.param('anon_dace_instance', 'H', '0', 'Kurucz', '1.0', (2100, 2400), (-8, -8), marks=pytest.mark.xfail)
    # too small temperature boundaries
])
def test_atom_download(instance, atom, charge, line_list, version,
                       temperature_boundaries,
                       pressure_boundaries,
                       request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = AtomClass(dace_instance)

    output_directory = '/tmp'
    output_filename = 'atom.tar.gz'
    instance.download(
        atom=atom, charge=charge, line_list=line_list, version=version,
        temperature_boundaries=temperature_boundaries,
        pressure_boundaries=pressure_boundaries,
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)
