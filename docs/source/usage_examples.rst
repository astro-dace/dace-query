Usage examples
==============

Filtering bad quality data
--------------------------

Before applying any scientific operation on the recovered data, it is important to ensure its quality by filtering out bad data points.

Unlike the `DACE website <https://dace.unige.ch>`_, which filters data automatically, with dace-query you must do it **manually**.

To do so, it is necessary to check the following parameters:

* The DRS quality check : ``drs_qc``
* The error on the radial velocity : ``rv_err``
* The Signal to Noise at order 50 of the CCD : ``sn50``


**Here is an example filtering out bad quality data :**

.. code-block:: python

    # Retrieve radial velocity timeseries for the HD40307 target
    result = Spectroscopy.get_timeseries(target='HD40307', sorted_by_instrument=False, output_format='numpy')

    # Filter based on :
    # * the radial velocities error
    # * the drs quality check
    # * the signal to noise at order 50 (if available).
    condition = (result['rv_err'] > 0.0) & (result['rv_err'] < 20.0) & \
            (result['drs_qc']) & \
            ((np.isnan(result['sn50'])) | (result['sn50'] > 20))


    # Apply the filter on the retrieved data
    filtered_data = dict(map(lambda pair: (pair[0], pair[1][condition]), result.items()))

    #  ... the equivalent more human-readable code
    filtered_data = {}
    for parameter, values in result.items():
        filtered_data[parameter] = values[condition]

Download non common data products from a CHEOPS visit
-----------------------------------------------------


.. versionadded:: 2.0.0

    Downloading data product is now done using the new :meth:`~dace_query.cheops.cheops.CheopsClass.download` method.

    By specifying the ``file_type`` parameter, you may now download specific data products for CHEOPS visits :

    .. code-block:: python

        from dace_query.cheops import Cheops

        visits = Cheops.download(
            'SCI_RAW_Attitude', 
            {'obj_id_catname': {'equal': 'HD88111'}}, 
            output_directory='/tmp', 
            output_filename='cheops.tar.gz' 
        )
    
    Also, the `CHEOPS module on the DACE web app <https://dace.unige.ch/cheopsDatabase>`_ has been updated so that all CHEOPS data products types can now be downloaded individually by using the 'custom' download option.



.. deprecated:: 2.0.0

    The following example is deprecated and will be removed in a future version of the library.

On the `DACE website <https://dace.unige.ch>`_, several data products per visit can be downloaded, such as light curves, images or many other types of files already defined.

But it is also possible for each of the cheops visits to **list all the data products**, to **select some non common** (like the Attitude, HkCentroid, ...) and then to **download them**.

With the dace-query package, this last one can be achieved thanks to the combination of different functions :

* ``Cheops.list_data_product(visit_filepath=...)``
* ``Cheops.download_files(file_type='files', files=...)``
* and some regular expressions using ``import re``

**Here is an example to download the "attitude" product files of a CHEOPS visit for the star HD88111 :**

.. code-block:: python

    import re
    from pathlib import Path
    from dace_query.cheops import Cheops

    # Retrieve one cheops visit for the target HD88111
    cheops_visits = Cheops.query_database(
        filters={
            'obj_id_catname': {
                'equal': ['HD88111']
            }
        },
        limit=1,
        output_format='dict')

    for visit in cheops_visits.get('file_rootpath', []):

        # Get all data products available for the raw file specified (=visit)
        visit_products = Cheops.list_data_product(
            visit_filepath=str(visit),
            output_format='dict'
        )

        # ... check if there are data products
        if (not visit_products) and visit_products.get('file', None):
            continue  # pass loop # log...


        # Get files containing "Attitude" in their name using regex
        files = [product for product in visit_products['file'] if
                re.match('.*Attitude.*', Path(product).name, re.IGNORECASE)]

        # ... check if there are files matching the regex
        if not files:
            continue  # pass loop # log...


        # Download the matched files
        Cheops.download_files(
            files=files,
            file_type='files',
            output_directory='/tmp',
            output_filename=f'{Path(visit).parent.name}.tar.gz'
        )
