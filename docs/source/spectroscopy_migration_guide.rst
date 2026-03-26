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

Changes in DRS Format
######################################################################################################

New format :
************

The new backend standardizes all DRS versions into the following format:

``DRS-X.Y.Z-METHOD`` 

* ``X.Y.Z``: Major, minor, and patch versions.
* ``METHOD``: Name of the DRS or post-process used.

.. dropdown:: Examples 
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    * ``DRS-3.3.10-CCF``: Standard processing extracting radial velocities from the CCF.
    * ``DRS-3.3.10-LBL``: Line-By-Line post-process using products from DRS-3.3.10.

Legacy formats :
****************

Previously, inconsistent formats (e.g., ``DRS-3.5`` vs ``DRS-3.3.10``) complicated sorting and filtering. Older versions are now renamed to match the new standard:

``D̶R̶S̶-̶3̶.̶5̶ → DRS-0.3.5-CCF``

Usage in the API :
******************

Internally, version strings are split into four fields for robust sorting: ``drs_major``, ``drs_minor``, ``drs_patch``, and ``rv_extraction_method``.

You can simply pass the full string (e.g., ``DRS-3.3.10-CCF``) or ``latest`` to the ``drs_version`` parameter. The API automatically parses it to handle the underlying filtering.

Changes in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database`
######################################################################################################

The :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database` method now returns a list of **raw frames** (observations), matching the behavior of the `DACE spectroscopy database <https://dace.unige.ch/spectroscopyDatabase/>`_. 

Unlike previous versions, which returned available points per instrument and DRS version, raw frames are now independent of the DRS. They represent a single observation of a target with a given instrument at a specific time.

Key updates:

* **Automatic name resolution:** ``target_name`` is automatically resolved using SIMBAD. If resolution fails, it matches the exact target name in the raw frame's ``.fits`` header.
* **Calibration frames:** These are now included by default and can be filtered using ``dpr_catg='CALIB'`` or ``dpr_catg='SCIENCE'``.

Example query for raw frames (observations) of ``HD69830`` with ``HARPS``:

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    
    filters : dict = {
        'target_name': { 'contains': ['HD69830'] },
        'instrument_name': { 'contains': ['HARPS'] }
    }
    raw_frames = Spectroscopy.query_database(filters=filters)

These raw frames can be used to identify points in :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.get_timeseries` or preview/download specific files via :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` or :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.browse_products`.

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
* :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.download` to download the files of your choice

Both of these methods accept the same filters as :meth:`~dace_query.spectroscopy.spectroscopy.SpectroscopyClass.query_database`

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

Radial Velocity Sources
***********************

Use the new ``rv_source`` parameter to select data from specific processing pipelines (e.g., ``PUBLICATIONS``, ``SKY_SUBTRACTED``, ``TELLURIC_CORRECTED``). By default, it returns both ``STANDARD_PROCESSING`` and ``PUBLICATION`` data.

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy, Source
    
    # Access telluric corrected RVs (e.g., for NIRPS)
    ts_telluric = Spectroscopy.get_timeseries(target='HD69830', rv_source=Source.TELLURIC_CORRECTED)

    # Exclude publication data by asking for only standard processing
    ts_standard = Spectroscopy.get_timeseries(target='HD69830', rv_source=Source.STANDARD_PROCESSING)

.. dropdown:: Read more about radial velocity sources
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: info

    Please see the :class:`~dace_query.spectroscopy.spectroscopy.Source` enum for a complete list of available radial velocity sources.

Handling DRS versions
*********************

Specify the DRS version via the ``drs_version`` parameter. Use ``latest`` for the most recent standard pipeline, or an exact string. When specifying an exact version, providing an explicit instrument prevents ambiguity.

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    
    # Latest DRS version per instrument
    ts_latest = Spectroscopy.get_timeseries(target='HD69830', drs_version='latest')
    
    # Specific DRS version
    ts_specific = Spectroscopy.get_timeseries(target='HD69830', drs_version='DRS-3.3.10')

.. dropdown:: Read more about DRS versions
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
