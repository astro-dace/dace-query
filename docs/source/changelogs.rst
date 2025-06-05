Changelogs
#################


.. dropdown:: 2.0.0 ``current``
    :open:
    :animate: fade-in-slide-down
    :color: info
    :icon: sparkle-fill

    * **Summary**
        * Version 2.0.0 introduces breaking changes as it transitions to a new backend for TESS and CHEOPS.
        * The CHEOPS download module has been reworked, as such, some functions are now deprecated.
        * The Sun webapp download functionality has been reworked (to be the same as the CHEOPS module).
        * The OpenData module has been phased out in favor of a new DOI module that will be released in the future.
        * Documentation has been fully reworked

    * **General changes**
        * Changed default file-output location to the current working directory (previously defaulted to home directory, which could introduce clutter).
        * Updated catalog module to align with backend changes :
            * Catalogs are moving to their own module.
            * This version introduces these changes for the CHEOPS and TESS catalogs.

    * **TESS Module**
        * New backend for TESS
        * Added access to TESS catalogs (TIC, TOI)
        * Reworked coordinate-search methods :
            * Compability with the new TESS backend.
            * Added support for TOI and TIC catalogs. (Meaning you may now search for TOIs using a cone search)
        * Updated documentation and examples

    * **CHEOPS Module**
        * New backend for CHEOPS
        * Download module has been reworked :
            * Deprecated old download functionalities in favor of a single download method :meth:`~dace_query.cheops.cheops.CheopsClass.download`
                * Deprecate : :meth:`~dace_query.cheops.cheops.CheopsClass.download_files`
                * Deprecate : :meth:`~dace_query.cheops.cheops.CheopsClass.download_diagnostic_movie`
            * Deprecate old product listing functionalities in favor of the new :meth:`~dace_query.cheops.cheops.CheopsClass.browse_products` method.
                * :meth:`~dace_query.cheops.cheops.CheopsClass.browse_products` Allows you to list all available data products for a given CHEOPS visit before downloading them.
                * Deprecate : :meth:`~dace_query.cheops.cheops.CheopsClass.list_data_product`
            * Faster downloads by disabling compression
                * Add the possibility to download files without compression using the new :meth:`~dace_query.cheops.cheops.CheopsClass.download_files` method with the ``compressed=False`` argument.
                * To keep backwards compatibility, the default value for ``compressed`` is set to ``True``.
                    * This is the default behavior of the previous version, which will return a ``tar.gz`` archive.
                * It is recommended to switch to ``compressed=False`` as this will largely increase download performance.
                * The output format will change based on the ``compressed`` argument:
                    * If ``compressed=True`` (default), the output will be a ``tar.gz`` file.
                    * If ``compressed=False``, the output will be a a ``.tar`` file
                * In regards to the size increase caused by using ``compressed=False`` : 
                    * Due to their binary structure and frequent use of data like floating-point arrays, FITS files typically compress poorly with gzip, resulting in marginal file size reduction.
                    * The size increase when using ``compressed=False`` is expected to be minimal, around 5-10% larger than the compressed version.
                    * This tradeoff is considered acceptable given the significant performance improvement in download speed.
        * Updated documentation and examples

    * **Exoplanets Module**
        * Now supports the new 'Atreides' catalog
            * You may use the :meth:`~dace_query.exoplanet.exoplanet.ExoplanetClass.query_database` method to query both catalogs.
            * By default, the PlanetS catalog is used so there is no impact on existing code.

    * **Sun Module**
        * The Sun module has been reworked to use the new backend.
        * The download functionality has been reworked to be the same as the CHEOPS module.
            * Deprecate the :meth:`~dace_query.sun.sun.SunClass.download_files` method in favor of the :meth:`~dace_query.sun.sun.SunClass.download` method.
        * The methods to download public data from the Sun database now query the server directly rather than interfacing through the API, which should improve performance. 
            * :meth:`~dace_query.sun.sun.SunClass.download_public_release_all`
            * :meth:`~dace_query.sun.sun.SunClass.download_public_release_ccf`
            * :meth:`~dace_query.sun.sun.SunClass.download_public_release_timeseries`

    * **Documentation**
        * New frontend and style
        * New, simpler navigation between modules
        * Rework the search functionality. (Use ``⌘+k`` on mac or ``ctrl+k`` on windows)
        * Updated the documentation with new examples and code snippets
        * Updated the TESS and CHEOPS modules in the docs to reflect the new backend and functionalities
        * Replaced large static lists with dropdowns to reduce visual clutter.
        * Refactored code snippets across all modules to support new styling
        * Added copy-to-clipboard function for code snippets

.. dropdown:: 1.2.3

    * Reverted the required setuptools version to below 77.0.0 due to changes in how the license is reported in ``pyproject.toml``. 
        * This avoids requiring a newer setuptools version that is not yet available in ``conda``.


.. dropdown:: 1.2.2

    * Fixed a bug where column names in the Simbad result of astroquery module were updated to be lowercase.
    * Changed "IDS" to "ids".

.. dropdown:: 1.2.1

    * New standalone webapp for the Sun module.
    * Sun.get_timeseries() is deprecated and has been removed. Use query_database() instead.

.. dropdown:: 1.2.0

    * New Hipparcos data in the Astrometry module
        * Query the Hipparcos catalog for a specific target : ``Astrometry.query_hipparcos_database()``
        * Query the Hipparcos Intermediate Astrometric Data (IAD) for a specific target : ``Astrometry.get_hipparcos_timeseries()``
    * Updated the tests that were failing due to previous updates in the databases

.. dropdown:: 1.1.0

    * Cheops module
        * List data products for a specified visit : ``Cheops.list_data_product()``
        * Download specific files using exact filenames: ``Cheops.download_files()``
    * Fixes
        * Duplicated log issue
        * Download issue (with the accessing results method)
    * Code improvements
    * Enhanced documentation


.. dropdown:: 1.0.1

    **The first public release of the dace-query package**

    * Use `dace <https://dace.unige.ch>`_'s rest endpoints to retrieve datas
    * Handle dace authentication using a **.dacerc** file
    * New modules added
        * astrometry
        * atmosphericSpectroscopy
        * catalog
        * cheops
        * cheops
        * exoplanet
        * imaging
        * lossy
        * monitoring
        * opacity
        * opendata
        * photometry
        * population
        * spectroscopy
        * sun
        * target
        * tess
