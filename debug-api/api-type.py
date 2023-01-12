from dace_query.dace import DaceClass

a = DaceClass()
print(type(a))

from dace_query.exoplanet import Exoplanet
from pandas import DataFrame

values: DataFrame = Exoplanet.query_database(output_format='pandas', limit=10)

print(type(values))
