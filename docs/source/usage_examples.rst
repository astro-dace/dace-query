Usage examples
##############

Filtering bad quality data
**************************

Before applying any scientific operation on the recovered data, it is important to ensure their good quality and therefore to filter out the bad ones.

There is not like on the `DACE website <https://dace.unige.ch>`_ a filter doing it automatically for you, with dace-query you will have to do it **manually**.

To do so, it is necessary to check the following parameters :

* The DRS quality check : ``drs_qc``
* The error on the radial velocity : ``rv_err``
* The Signal to Noise at order 50 of the CCD : ``spectroFluxSn50``


**Here is an example filtering bad quality data to keep only the good ones :**


.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    import numpy as np

    # Retrieve radial velocity timeseries for the HD40307 target
    result = Spectroscopy.get_timeseries(target='HD40307', sorted_by_instrument=False, output_format='numpy')

    # Filter based on :
    # * the radial velocities error
    # * the drs quality check
    # * the signal to noise at order 50 (if available).
    condition = (result['rv_err'] > 0.0) & (result['rv_err'] < 20.0) & \
            (result['drs_qc']) & \
            ((np.isnan(result['spectroFluxSn50'])) | (result['spectroFluxSn50'] > 20))

    # Apply the filter on the retrieved data
    filtered_data = dict(map(lambda pair: (pair[0], pair[1][condition]), result.items()))

    #  ... the equivalent more human-readable code
    filtered_data = {}
    for parameter, values in result.items():
        filtered_data[parameter] = values[condition]