from pathlib import Path

from dace_query import DaceClass
from dace_query.opacity import AtomClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = AtomClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc)
)
# Atom.download('Lu', 0, 'Kurucz', 1.0, (2500, 2600), (-8, -8), output_directory='/tmp',
#              output_filename='test_atom.tar.gz')
# v =  Atom.get_high_resolution_data('Lu', 0, 'Kurucz', 1.0, 2500, -8, (1.01, 3.02))

# Atom.interpolate('Lu', 0, 'Kurucz', 1.0, [2510], output_directory='/tmp', output_filename='opacity_atom_interpolate.tar.gz')

x = instance.get_data('Lu', '0', 'Kurucz', '1.0', temperature=2500, pressure_exponent=-8)
print(x.keys())

x = instance.get_high_resolution_data('Lu', '0', 'Kurucz', '1.0', 2500, -8, (60000, 60001))
print(len(x['opacity']))
