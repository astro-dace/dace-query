dev (1.1.0)
***********

* Cheops module
    * List data products for a specified visit : ``Cheops.list_data_product()``
    * Download specific files using exact filenames: ``Cheops.download_files()``
* Fixes
    * Duplicated log issue
    * Download issue (with the accessing results method)
* Code improvements
* Enhanced documentation


1.0.1
*****

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
