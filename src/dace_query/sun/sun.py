from __future__ import annotations

import datetime
import json
import logging
from typing import Optional

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass
from dace_query.dace import NoDataException
from dace_query.spectroscopy import Spectroscopy

SUN_DEFAULT_LIMIT = 200000


class SunClass:
    """
    The sun class.
    Use to retrieve data from the sun module.

    .. tip::
    
        A sun instance is already provided, to use it :
        
        .. code-block:: python
        
            from dace_query.sun import Sun

    """

    __ACCEPTED_FILE_TYPES = ['s1d', 's2d', 'ccf', 'all']
    __SUN_RELEASE_FULL_URL_TIMESERIES = "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_timeseries_2015-2018.tar.gz"
    __SUN_RELEASE_URL_PREFIX = "https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package"
    __SUN_RELEASE_URL_SUFFIX_ALL = "s1d_s2d_ccf"
    __SUN_RELEASE_URL_SUFFIX_CCF = "ccf"
    __SUN_RELEASE_URL_EXT = ".tar.gz"

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable sun object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.sun import SunClass
            sun_instance = SunClass()

        """
        self.__SUN_API = "sun-webapp"
        self.__OBS_API = "obs-webapp"

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"sun-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(
        self,
        limit: Optional[int] = SUN_DEFAULT_LIMIT,
        filters: Optional[dict] = None,
        sort: Optional[dict] = None,
        output_format: Optional[str] = None,
    ):
        """
        Query the sun database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting all sun data
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                values = Sun.query_database()

        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__SUN_API,
                endpoint="search",
                params={
                    "limit": str(limit),
                    "filters": json.dumps(filters),
                    "sort": json.dumps(sort),
                },
            ),
            output_format=output_format,
        )

    # def get_timeseries(self, output_format: Optional[str] = None):
    #     """
    #     Get all sun timeseries.

    #     All available formats are defined in this section (see :doc:`output_format`).

    #     :param output_format: Type of data returns
    #     :type output_format: Optional[str]
    #     :return: The desired data in the chosen output format

    #     >>> from dace_query.sun import Sun
    #     >>> values = Sun.get_timeseries()
    #     """
    #     return self.dace.transform_to_format(
    #         self.dace.request_get(
    #             api_name=self.__SUN_API,
    #             endpoint="sun/radialVelocities",
    #         ),
    #         output_format=output_format,
    #     )

    def download(
        self,
        file_type: str,
        filters: Optional[dict] = None,
        compressed: Optional[bool] = True,
        output_directory: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> None:
        """
        Download Sun spectroscopy products (S1D, S2D, ...).

        .. dropdown:: Available spectroscopy product types
            :color: info
            :icon: list-unordered
            :open:
            
            .. list-table::
               :header-rows: 1
               :widths: auto
            
               * - file_type
                 - description
               * - ``'s1d'``
                 - Extracted merged-1d spectra, corrected from the instrumental blaze, in the Sun's rest-frame.
               * - ``'s2d'``
                 - Extracted echelle-order 1d spectra, corrected from the instrumental blaze, in the Earth rest-frame.
               * - ``'ccf'``
                 - Cross Correlation Function (CCF) obtained by cross-correlating the S2D spectra with a synthetic mask optimised for the Sun.
               * - ``'all'``
                 - Complete product set.
            
            See the `Product description document on DACE <https://dace.unige.ch/sun/pdf/README.pdf>`_ for more details.

        .. dropdown:: Specifying compression behavior
            :color: success
            :icon: info
            
            You can control the compression behavior of the downloaded files using the ``compressed`` parameter.
        
            By default, files will be compressed into a ``.tar.gz`` archive if multiple files are downloaded.
            
            If you want to disable compression, set the ``compressed`` parameter to ``False``. 
            (will result in a ``.tar`` archive).
            
            If you want to force compression, set the ``compressed`` parameter to ``True``. 
            (will result in a ``.tar.gz`` archive).
            
            When downloading large datasets, it is recommended to disable compression by setting ``compressed=False``.
            This will speed up the download process and reduce memory usage but will result in a larger file size.
    
        **Output directory** is the location where the downloaded files will be saved.
        
        **Output filename** is the name of the downloaded file. If not specified, a default name will be used.

        .. note::
        
            When specifying ``output_filename``, be mindful of the appropriate file extension:
            
            When downloading a **single file** : match the extension to the file type (e.g., ``output_filename="lightcurve.fits"``) or leave ``output_filename`` as ``None`` to use the default name
            When downloading **multiple files** : use a ``.tar`` or ``.tar.gz`` extension (e.g., ``output_filename="my_data.tar.gz"``) or leave ``output_filename`` as ``None`` to use the default name

        :param file_type: The type of files to download
        :type file_type: str
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param compressed: Specify whether to compress the downloaded files. (``True`` for ``.tar.gz``, ``False`` for ``.tar``)
        :type compressed: Optional[bool]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading sun spectroscopy products using a filepath
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                filters_to_use = {'file_rootpath': {'contains': ['r.HARPN.2016-01-03T15-36-20.496.fits']}}
                Sun.download('s1d', filters=filters_to_use, output_directory='/tmp', output_filename='sun_spectroscopy_data.tar.gz')
        
        .. dropdown:: Downloading sun spectroscopy products using a specific date
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                filters_to_use = {'date_night': {'contains': ['2016-12-10']}}
                Sun.download('s1d', filters=filters_to_use)
        """

        if file_type not in self.__ACCEPTED_FILE_TYPES:
            raise ValueError(
                "file_type must be one of these values : "
                + ",".join(self.__ACCEPTED_FILE_TYPES)
            )
        if filters is None:
            filters = {}

        download_id = self.dace.request_post(
            api_name=self.__SUN_API,
            endpoint='download/key',
            data=json.dumps({
                'fileType': file_type,
                'filters': filters,
                })
        )
        if not download_id:
            return None

        self.dace.persist_file_on_disk(
            api_name=self.__SUN_API,
            obs_type='spectroscopy',
            params={'compressed': compressed},
            download_id=download_id['key'],
            output_directory=output_directory,
            output_filename=output_filename
        )
        

    def download_files(
        self,
        file_type: Optional[str] = "s1d",
        files: Optional[list[str]] = None,
        output_directory: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> None:
        """
        .. deprecated:: 2.0.0
            This method is deprecated and will be removed in a future version. Use :meth:`download` with ```filters``` instead :
            
            .. code-block:: python
            
                files = ['harpn/DRS-3.0.1/reduced/2018-07-16/r.HARPN.2018-07-17T08-10-32.225.fits']
                filters: dict = { 'file_rootpath': {'contains': files} }
                Sun.download(file_type='s1d', filters=filters)
        
        Download reduction products specified in argument for the list of raw files specified and save it locally.

        .. dropdown:: Available spectroscopy product types
            :color: info
            :icon: list-unordered

            .. list-table::
               :header-rows: 1
               :widths: auto
            
               * - file_type
                 - description
               * - ``'s1d'``
                 - Extracted merged-1d spectra, corrected from the instrumental blaze, in the Sun's rest-frame.
               * - ``'s2d'``
                 - Extracted echelle-order 1d spectra, corrected from the instrumental blaze, in the Earth rest-frame.
               * - ``'ccf'``
                 - Cross Correlation Function (CCF) obtained by cross-correlating the S2D spectra with a synthetic mask optimised for the Sun.
               * - ``'all'``
                 - Complete product set.
            
            See the `Product description document on DACE <https://dace.unige.ch/sun/pdf/README.pdf>`_ for more details.


        :param file_type: The type of files to download
        :type file_type: Optional[str]
        :param files: The raw files
        :type files: list[str]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading sun spectroscopy products given a list of files
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                files_to_retrieve = ['harpn/DRS-2.3.5/reduced/2016-01-03/r.HARPN.2016-01-03T15-36-20.496.fits']
                Sun.download_files('s1d', files=files_to_retrieve, output_directory='/tmp', output_filename='files.tar.gz')

        """
        if files is None:
            raise NoDataException

        files = list(
            map(
                lambda file: f"{file}.fits" if not file.endswith(".fits") else file,
                files,
            )
        )

        download_response = self.dace.request_post(
            api_name=self.__OBS_API,
            endpoint="download/prepare/sun",
            data=json.dumps({"fileType": file_type, "files": files}),
        )
        if not download_response:
            return None
        download_id = download_response["values"][0]
        self.dace.persist_file_on_disk(
            api_name=self.__OBS_API,
            obs_type="sun",
            download_id=download_id,
            output_directory=output_directory,
            output_filename=output_filename,
        )

    def download_public_release_all(
        self,
        year: str,
        month: str,
        output_directory: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> None:
        """
        Download public sun data of year and month specified in arguments.

        :param year: The year for sun data
        :type year: str
        :param month: The month for sun data
        :type month: str
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading public sun data for a given year and month
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                Sun.download_public_release_all('2015', '12')  # Downloads the sun data for December 2015

        """
        try:
            START_DATE = datetime.date(2015, 7, 1)
            END_DATE = datetime.date(2018, 7, 1)
            GIVEN_DATE = datetime.date(int(year), int(month), 1)
        except ValueError as e:
            raise ValueError("Year and month must be valid. ", e)

        if not (START_DATE <= GIVEN_DATE <= END_DATE):
            raise ValueError("The only available dates are between 2015-07-01 and 2018-07-01.")
            
        year_and_month = GIVEN_DATE.strftime("%Y-%m") # Format the date as 'YYYY-MM'

        # Ex: https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package_s1d_s2d_ccf_2018-03.tar.gz
        url = f"{self.__SUN_RELEASE_URL_PREFIX}_{self.__SUN_RELEASE_URL_SUFFIX_ALL}_{year_and_month}{self.__SUN_RELEASE_URL_EXT}"
        self.dace.download_static_file_from_url(url, output_directory=output_directory, output_filename=output_filename)
        

    def download_public_release_ccf(
        self,
        year: str,
        output_directory: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> None:
        """
        Download public ccf data realease of year specified in argument.

        :param year: The year for the ccf data
        :type year: str
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading public ccf data for a given year
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                Sun.download_public_release_ccf('2015') # Downloads the CCF data for 2015
        """
        year = str(year)
        if year not in ["2015", "2016", "2017", "2018"]:
            raise ValueError("The only available years are '2015', '2016', '2017', '2018'.")
        
        # Ex: https://dace.unige.ch/downloads/sun_release_2015_2018/harpn_sun_release_package_ccf_2016.tar.gz
        url = f"{self.__SUN_RELEASE_URL_PREFIX}_{self.__SUN_RELEASE_URL_SUFFIX_CCF}_{year}{self.__SUN_RELEASE_URL_EXT}"
        self.dace.download_static_file_from_url(url, output_directory=output_directory, output_filename=output_filename)

    def download_public_release_timeseries(
        self,
        period: Optional[str] = "2015-2018",
        output_directory: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> None:
        """
        Download public timeseries data release for a specified period and save it locally.

        The only available period is ``'2015-2018'``.

        :param period: The period
        :type period: Optional[str]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading public timeseries data
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.sun import Sun
                Sun.download_public_release_timeseries() # Downloads the timeseries data from 2015 to 2018
        """
        if period != "2015-2018":
            raise ValueError("The only available period is '2015-2018'.")
        
        url = f"{self.__SUN_RELEASE_FULL_URL_TIMESERIES}"
        self.dace.download_static_file_from_url(url, output_directory=output_directory, output_filename=output_filename)


Sun: SunClass = SunClass()
"""
This is a singleton instance of the :class:`SunClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.sun import Sun
"""
