from pathlib import Path

from dace_query import DaceClass
from dace_query.population import PopulationClass

fp_config = Path('../tests/config.ini')
fp_dacerc = Path('../tests/dev.dacerc')

instance = PopulationClass(
    dace_instance=DaceClass(
        config_path=fp_config,
        dace_rc_config_path=fp_dacerc))

x = instance.get_columns('ng76')

print(x['name'])

'''
x = Population.get_snapshot_ages()
print(x)

from dace.population import Population

pop_id, planet_id, system_id = 'ng96', 1, 1
parameters_to_retrieve = ['time_yr', 'total_mass']
values = Population.get_track(population_id=pop_id, system_id=system_id, planet_id=planet_id,
                              columns=parameters_to_retrieve)
'''
