import numpy as np

from dace_query.spectroscopy import Spectroscopy

result = Spectroscopy.get_timeseries(
    target='HD40307',
    sorted_by_instrument=False,
    output_format='numpy')

print(result)

# condition = (np.isnan(result['spectroFluxSn50']) | result['spectroFluxSn50'] > 20)
# filtered_data = dict(map(lambda pair: (pair[0], pair[1][condition]), result.items()))
# y = np.logical_or(np.isnan(result['spectroFluxSn50']), result['spectroFluxSn50'] > 20)
condition = (result['rv_err'] > 0.0) & (result['rv_err'] < 20.0) & \
            (result['drs_qc']) & \
            ((np.isnan(result['spectroFluxSn50'])) | (result['spectroFluxSn50'] > 20))

print(condition)

'''
filter_condition = (result['rv_err'] > 0.0) & (result['rv_err'] < 20.0) & (result['spectroFluxSn50'] > 20) & (
    result['drs_qc'])
filtered_data = dict(map(lambda pair: (pair[0], pair[1][filter_condition]), result.items()))

# Equivalent human-readable code
filter_condition = (result['rv_err'] > 0.0) & (result['rv_err'] < 20.0) & (result['spectroFluxSn50'] > 20) & (
    result['drs_qc'])
filtered_data = {}
for parameter, values in result.items():
    filtered_data[parameter] = values[filter_condition]

print(filtered_data)
'''
