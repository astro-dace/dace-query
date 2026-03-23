===================================================
dace-query 3.0.0 Migration Guide
===================================================

With version ``dace-query==3.0.0``, we introduce a new backend for the Spectroscopy module, which has led to changes in the available parameters and their names.

This document provides a guide to migrating your code from previous versions of the dace-query package to version ``3.0.0`` and onwards.

Timeframe for migration
##########################
First of all, **we will maitain the old backend for a transition period, so that you can update your code at your own pace.**
During this transition period we will keep ingesting instrument data into both backends (until September 2026).

.. dropdown:: Timeline for migration
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: calendar

    +---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Timeline Date (estimated) | Description                                                                                                                                                                                                                |
    +===========================+============================================================================================================================================================================================================================+
    | ``2026-03``               | Release of ``dace-query 3.0.0`` with the new backend for the ``Spectroscopy`` module.                                                                                                                                      |
    +---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ``2026-09``               | Stop ingesting instrument data into the old backend. ``dace-query<3.0.0`` remains online and functional, but no new data will be added to it. You will need to migrate to obtain data from ``2026-09-01`` and onwards.     |
    +---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ``TBD (>2027)``           | Deprecation of the old backend. After this point, the old backend will no longer be accessible, and you will need to have migrated your code to use the new backend to access ``Spectroscopy`` data.                       |
    +---------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

    If you need assistance with the migration, please do not hesitate to reach out to us at `dace-support@unige.ch <mailto:dace-support@unige.ch>`_.

Changes in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database`
######################################################################################################
The :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database` method is now returns a list of **raw frames**.
This exhibits the same behavior as on the spectroscopy database on DACE : https://dace.unige.ch/spectroscopyDatabase/
As such, a lot of parameters have changed.

This is a big departure from the previous version, where the :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database` method returned a list of available points per instrument and per DRS version.
Now the returned list of raw frames are independant of DRS and simply represent an observation of a given target with a given instrument at a given time.
The :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` or :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.browse_products` methods can be used to download or preview the files associated with a given raw frame for various DRS versions.

One key difference is that ``target_name`` is resolved automatically using SIMBAD. If a target is unable to be resolved this way, this method will still return results that match the exact target name specified in the raw frame's .fits header.

This was done to simplify the query process and handling of multiple DRS versions and post-processings.

For example if you want to find all the raw frames available for the target ``HD69830`` and the instrument ``HARPS`` you may do :

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    
    filters : dict = {
        'target_name': { 'contains': ['HD69830'] },
        'instrument_name': { 'contains': ['HARPS'] }
    }
    raw_frames = Spectroscopy.query_database(filters=filters)

Which will fetch a list of raw frames (observations) matching the specified filters.
Note that calibration frames are now included in the query results, and can be filtered using the ``dpr_catg='CALIB'`` or ``dpr_catg='SCIENCE'`` in the query results.

You can use this list of raw frames to then identify specific points in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries` or specific files to download in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` or :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.browse_products`.

.. dropdown:: Read more about :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database`
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    Please see the :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database` documentation for more details about the available filters and how to use them.

Changes in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` functionalities
######################################################################################################

With version ``3.0.0`` we have reworked the download functionalities of the Spectroscopy module to simplify the download process and make it more efficient.

The old  :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download_files` is now deprecated in favor of :

* :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.browse_products` to preview files for a given observation
* :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` to download the files of your choice in a single step.

Handling DRS versions
*******************************
You can now specify the DRS version of the data you want to download using the new ``drs_version`` parameter 
in both :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` and :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.browse_products` methods.

You may use ``drs_version='latest'`` to get reduced products from the latest DRS version available for each instrument.

Or you can specify a specific DRS version (e.g. ``drs_version='DRS-3.3.10'``).

.. dropdown:: Note
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download_files` is deprecated, will remain functional but inneficient as it will perform multiple API calls to download the files. **It will eventually be removed so it is recommended to switch to the new download method.**


Changes in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries`
######################################################################################################


Handling various radial velocity sources (e.g. ``PUBLICATIONS``, ``SKY_SUBTRACTED`` or ``TELLURIC_CORRECTED`` etc.)
******************************************************************************************************************************

You may now specify query data coming from various radial velocity sources using the new ``rv_source`` parameter in the :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries` method.

This allows you, for example, to access the telluric corrected radial velocities for NIRPS data :

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy, Source
    
    # Get timeseries for the latest DRS version available per instrument
    timeseries = Spectroscopy.get_timeseries(target='HD69830', rv_source=Source.TELLURIC_CORRECTED)


Or for example if you want to exclude publication data from your query results :

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy, Source
    
    # Get timeseries for the latest DRS version available per instrument
    timeseries = Spectroscopy.get_timeseries(target='HD69830', rv_source=Source.STANDARD_PROCESSING)


By default, the ``rv_source`` parameter is set to ``STANDARD_PROCESSING`` and ``PUBLICATION`` which will return results from both the standard DRS and from scientific publications.

.. dropdown:: Read more about radial velocity sources
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    Please see the :class:`~dace_query.spectroscopy.spectroscopy.Source` enum for a complete list of available radial velocity sources.

Handling DRS versions
*******************************
You can now specify the DRS version of the data you want to access using the new ``drs_version`` parameter in the :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries` method. 

You may use ``drs_version='latest'`` to get the timeseries for the latest DRS version available for each instrument.

Or you can specify a specific DRS version (e.g. ``drs_version='DRS-3.3.10'``). Note that it is recommended to specify an explicit instrument in that case to avoid ambiguity between instrument's DRS versions.


.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    
    # Get timeseries for the latest DRS version available per instrument
    timeseries = Spectroscopy.get_timeseries(target='HD69830', drs_version='latest')
    
    # Ge timeseries for a specific DRS version (e.g. DRS-3.3.10)
    timeseries = Spectroscopy.get_timeseries(target='HD69830', drs_version='DRS-3.3.10')


.. dropdown:: Read more about radial velocity sources
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    Please see the :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries` documentation for more details about the available options for the ``drs_version`` parameter.


Changes in parameters
**********************
As we introduce a new backend, the names of some parameters have changed, and some new parameters have been added. The following table summarizes the changes:

.. include:: _includes/spectroscopy_migration_table.rst


.. dropdown:: Read more about available parameters in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries`
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info
    
    There are now many more filterable parameters available in the new backend, which are not listed in the table above. 
    For a complete list of available parameters, please refer to the following page : :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries`.
