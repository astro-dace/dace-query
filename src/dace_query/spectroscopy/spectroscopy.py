from __future__ import annotations

from enum import Enum
import json
import logging
import re
import warnings

from typing import Union, Optional
from astropy.coordinates import SkyCoord, Angle
from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass
from dace_query.dace import NoDataException

SPECTROSCOPY_DEFAULT_LIMIT = 10000


def _adapt_legacy_file_type(file_type: Optional[Union[str, list[str]]]) -> Optional[Union[str, list[str]]]:
    """Convert legacy file type to new file type(s) used by the API."""

    if file_type is None:
        return None

    if isinstance(file_type, list):
        return file_type

    file_type_map: dict[str, list[str]] = {
        's1d': ['S1D_A', 'S1D_B'],
        's2d': ['S2D_A', 'S2D_B'],
        'ccf': ['CCF_A', 'CCF_B'],
        'all': [],
    }

    return file_type_map.get(file_type, file_type)

class Source(Enum):
    """
    Enumeration of the different sources of radial velocity data.
    Used to filter radial velocity time series data based on their source or method of rv extraction.
    See :meth:`SpectroscopyClass.get_timeseries` for usage examples.

    .. dropdown:: Available radial velocity sources
        :color: info
        :icon: info
        :open:
    
        Some DRS or postprocesses may be marked as ``Private`` if they are not publicly available.
        To access private data, ensure you have the necessary permissions and `authentication <dace_introduction.html#authentication>`_.

        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | Name                      | Value                     | Description                                                                                | Public/Private |
        +===========================+===========================+============================================================================================+================+
        | ``STANDARD_PROCESSING``   | ``"POSTDRS_A"``           | Standard DRS pipeline processing, RVs extracted from CCF.                                  | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``TELLURIC_CORRECTION``   | ``"POSTDRS_TELL_CORR_A"`` | Standard DRS pipeline processing, RVs extracted from CCF with telluric correction applied. | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``SKYSUB``                | ``"POSTDRS_SKYSUB_A"``    | Standard DRS pipeline processing, RVs extracted from CCF with sky subtraction applied.     | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``PUBLICATION``           | ``"PUB"``                 | RVs imported from publications.                                                            | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``SBART``                 | ``"SBART"``               | RVs extracted using the SBART method.                                                      | ``Private``    |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        + ``LBL``                   | ``"LBL"``                 | RVs extracted using the LBL method.                                                        | ``Private``    |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        
    .. dropdown:: Filtering radial velocity time series data by source
        :color: info
        :icon: list-unordered
    
        **Getting only telluric corrected radial velocity data:**
        
        .. code-block:: python

            from dace_query.spectroscopy import Spectroscopy
                timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Spectroscopy.Source.TELLURIC_CORRECTION])
                
        **Getting standard and publication radial velocity data:**
        
        .. code-block:: python
        
            from dace_query.spectroscopy import Spectroscopy
                timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Spectroscopy.Source.STANDARD_PROCESSING, Spectroscopy.Source.PUBLICATION])
    """
    STANDARD_PROCESSING = "POSTDRS_A"
    TELLURIC_CORRECTION = "POSTDRS_TELL_CORR_A"
    SKYSUB = "POSTDRS_SKYSUB_A"
    SBART = "SBART"
    LBL = "LBL"
    PUBLICATION = "PUB"

class SpectroscopyClass:    
    """
    The spectroscopy class.
    Use to retrieve data from the spectroscopy module.


    .. tip::
    
        A spectroscopy instance is already provided, to use it:
        
        .. code-block:: python

            from dace_query.spectroscopy import Spectroscopy

    """
    __VALID_FILE_TYPE_ABBREVIATIONS = ['s1d', 's2d', 'ccf', 'all']

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable spectroscopy object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.spectroscopy import SpectroscopyClass
            spectroscopy_instance = SpectroscopyClass()
        """
        self.__SPECTROSCOPY_API = 'spectroscopy-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"spectroscopy-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self,
                       limit: Optional[int] = SPECTROSCOPY_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the spectroscopy database to retrieve data in the chosen format.

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

        .. dropdown:: Getting all spectroscopy data
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                values = Spectroscopy.query_database()

        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__SPECTROSCOPY_API,
                endpoint='/search/',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }
            ), output_format=output_format
        )

    def query_region(self,
                     sky_coord: SkyCoord,
                     angle: Angle,
                     limit: Optional[int] = SPECTROSCOPY_DEFAULT_LIMIT,
                     filters: Optional[dict] = None,
                     output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query a region, based on SkyCoord and Angle objects, in the spectroscopy database and retrieve data in the chosen format.

        Filters can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param sky_coord: Sky coordinates object from the astropy module
        :type sky_coord: SkyCoord
        :param angle: Angle object from the astropy module
        :type angle: Angle
        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Searching for spectroscopy data using a cone search
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                from astropy.coordinates import SkyCoord, Angle
                sky_coord, angle = SkyCoord("23h13m16s", "+57d10m06s", frame='icrs'), Angle('0.045d')
                values = Spectroscopy.query_region(sky_coord=sky_coord, angle=angle)
        """
        coordinate_filter_dict = self.dace.transform_coordinates_to_dict(sky_coord, angle)
        filters_with_coordinates = {}
        if filters is not None:
            filters_with_coordinates.update(filters)
        filters_with_coordinates.update(coordinate_filter_dict)
        return self.query_database(limit=limit, filters=filters_with_coordinates, output_format=output_format)

    def download(self,
                 filters: dict,
                 file_type: Optional[str] = None,
                 compressed: Optional[bool] = False,
                 output_directory: Optional[str] = None,
                 output_filename: Optional[str] = None):
        """
        Download spectroscopy reduction products (S1D, S2D, ...) and save them locally.

        **Before downloading:** Use :meth:`browse_products` with identical parameters to preview 
        what files would be downloaded. This is particularly useful for large data sets.

        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the spectroscopy database.
        **Filters** can be applied to the query via named arguments (see :doc:`query_options`).
            
        .. dropdown:: Setting filters
            :color: primary
            :icon: code-square
        
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}


        .. dropdown:: Available file types
            :color: info
            :icon: list-unordered

            To check for available file types, you can use the :meth:`browse_products` method.

        Files are sent in different formats based on the number of files to download:

        - **Single file**: native format (e.g. ``.fits``)
        - **Multiple files**: archive (``.tar`` or ``.tar.gz``)

        .. dropdown:: Specifying compression behavior
            :color: success
            :icon: info

            You can control the compression behavior of multi-file downloads using the ``compressed`` parameter.

            - ``compressed=True`` produces a ``.tar.gz`` archive
            - ``compressed=False`` produces a ``.tar`` archive

            When downloading large datasets, disabling compression (``compressed=False``) may reduce CPU usage
            and speed up the download at the cost of larger files.

        :param filters: Filters to apply to the query
        :type filters: dict
        :param file_type: The type of files to download (see "Available file types")
        :type file_type: Optional[str]
        :param compressed: Whether to return a compressed archive when multiple files are downloaded
        :type compressed: Optional[bool]
        :param output_directory: The directory where files will be saved (defaults to the current working directory)
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download (defaults to the server-provided filename)
        :type output_filename: Optional[str]
        :return: None
        :rtype: None

        .. dropdown:: Downloading all available products for a specific observation (raw frame)
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                filters_to_use = {'file_rootname': {'contains':['HARPS.2010-04-04T03:38:51.386']}}
                Spectroscopy.download(filters=filters_to_use)

        .. dropdown:: Downloading products using a list of raw frames
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                
                # Let's say we want to get a list of all observations (raw frames) for 'HR3259' on '2018-11-03'
                raw_frame_filters = dict(target_name=dict(equal=['HR3259']), date_night=dict(equal=['2018-11-03']))
                raw_frames = Spectroscopy.query_database(filters=raw_frame_filters, output_format='dict')

                # Get the unique ids of those raw frames
                spectrum_ids = raw_frames.get('spectrum_id')

                # Pass the list of ids to download() to get all products for those spectra
                if spectrum_ids:
                    Spectroscopy.download(filters={'spectrum_id':{'equal':spectrum_ids}})


        .. dropdown:: Downloading all ``CCF_A`` files for a given target name
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                filters = {'target_name':{'equal': [target_name]}}
                Spectroscopy.download(file_type='CCF_A', filters=filters)
        """
        if filters is None:
            filters = {}
                        
        # Add support for legacy file type abbreviations (s1d, s2d, ccf, all)
        corrected_file_type = _adapt_legacy_file_type(file_type)
                        
        response = self.dace.request_post(
            api_name=self.__SPECTROSCOPY_API,
            endpoint='download',
            data=json.dumps({
                'fileType': corrected_file_type,
                'filters': filters
            })
        )
        
        download_id = response.get('key', None)
        
        if not download_id:
            return None


        self.dace.download_file(
            api_name=self.__SPECTROSCOPY_API,
            endpoint=f'download/{download_id}',
            params={'compressed': compressed},
            output_directory=output_directory,
            output_filename=output_filename
        )

    def download_files(self,
                       files: list,
                       file_type: Optional[str] = 'all',
                       output_directory: Optional[str] = None,
                       output_filename: Optional[str] = None):
        """
        .. deprecated:: 3.0.0
        
            This method is no longer supported and will be removed in a future version.
            Use :meth:`download` instead.
        
        Download reduction products specified in argument for the list of raw files specified and save it locally.
        
        .. dropdown:: Available file types
            :color: info
            :icon: list-unordered
            :open:
        
            * ``'s1d'``
            * ``'s2d'``
            * ``'ccf'``
            * ``'all'``

        :param files: The raw files
        :type files: list[str]
        :param file_type: The type of files to download
        :type file_type: Optional[str]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: Downloading reduction products for a list of raw files
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                files_to_download = ['harps/DRS-3.5/reduced/2019-07-05/HARPS.2019-07-06T04:00:00.323.fits']
                Spectroscopy.download_files(files=files_to_download, file_type='all')
        """

        if files is None:
            raise NoDataException


        if file_type not in self.__VALID_FILE_TYPE_ABBREVIATIONS:
            raise ValueError(f"file_type must be one of {self.__VALID_FILE_TYPE_ABBREVIATIONS}")

        # Legacy support warnings, 'bis' and 'guidance' file types are no longer in the db
        if file_type == 'guidance' : self.log.warning("The 'guidance' and 'bis' file types are no longer supported."); return
        if file_type == 'bis' : self.log.warning("The 'bis' file type is no longer supported."); return

        warnings.warn(
            "The 'download_files' method is deprecated and will be removed in a future version. "
            "Please use the 'download' method instead.",
            DeprecationWarning, 
            stacklevel=2
        )

        # Since the API expects raw file names, we need to extract them from the 'legacy' full paths.
        # Regex to extract the raw file from a full path : harps/DRS-3.5/reduced/2019-07-05/HARPS.2019-07-06T04:00:00.323.fits -> HARPS.2019-07-06T04:00:00.323
        raw_file_regex = re.compile(r'(?P<file_rootname>[A-Z]+\.\d{4}[:-]\d{2}[:-]\d{2}T\d{2}[:-]\d{2}[:-]\d{2}\.\d+)\.fits')
        
        # Apply the regex to all files in the list, extracting the raw file name
        file_rootnames = [
            match.group('file_rootname') 
            for file in files 
            if (match := raw_file_regex.search(file)) is not None
        ]
        
        filters = {'file_rootname': {'contains': file_rootnames}}

        # Fetch all matching raw frames
        raw_frames = self.query_database(filters=filters, output_format='dict')
        spectrum_ids = raw_frames.get('spectrum_id', [])
        
        if not spectrum_ids:
            self.log.warning("No matching raw frames found for the provided files.")
            return
        
        # Add support for legacy file type abbreviations (s1d, s2d, ccf, all)
        corrected_file_type = _adapt_legacy_file_type(file_type)
        
        # Use the download method to get the desired products for the found raw frames
        self.download(
            file_type=corrected_file_type,
            filters={'spectrum_id': {'equal': spectrum_ids}},
            output_directory=output_directory,
            output_filename=output_filename,
            compressed=True
        )

    def get_timeseries(self, 
                       target: str,
                       limit: Optional[int] = SPECTROSCOPY_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       sorted_by_instrument: Optional[bool] = True,
                       rv_sources: Optional[list[Source]] = [Source.STANDARD_PROCESSING, Source.PUBLICATION],
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Retrieve the spectroscopy time series data for a specified target in the chosen format.

        Filters can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).
        
        Using ``sorted_by_instrument=True`` will sort the results by ``instrument > drs > instrument_mode``
        and return a nested dictionary structure as shown in the sample output below.
        
        **Note :** when using ``sorted_by_instrument=True``, the ``output_format`` argument is ignored.
        
        
        .. dropdown:: Sample output with ``sorted_by_instrument=True``
            :color: info
            :icon: info
            
            .. code-block:: python
            
                    {
                        'HARPS15': {
                            'DRS-3.3.6': {
                                'EGGS': {
                                    'rjd': [...],
                                    'rv': [...],,
                                    ...
                                },
                                'HARPS': {
                                    'rjd': [...],,
                                    'rv': [...],,
                                    ...
                                }
                            },
                            'DRS-3.3.10': {
                                ...
                            }
                        },
                        'ESPRESSO19': {
                            ...
                        }
                    }

        The ``rv_sources`` argument allows to filter the radial velocity data based on their source or method of extraction.
        See the :class:`Source` enum for available options and usage examples.
        
        .. dropdown:: Available radial velocity sources
            :color: info
            :icon: info
            :open:
        
            Some DRS or postprocesses may be marked as ``Private`` if they are not publicly available.
            To access private data, ensure you have the necessary permissions and `authentication <dace_introduction.html#authentication>`_.

            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | Name                      | Value                     | Description                                                                                | Public/Private |
            +===========================+===========================+============================================================================================+================+
            | ``STANDARD_PROCESSING``   | ``"POSTDRS_A"``           | Standard DRS pipeline processing, RVs extracted from CCF.                                  | ``Public``     |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | ``TELLURIC_CORRECTION``   | ``"POSTDRS_TELL_CORR_A"`` | Standard DRS pipeline processing, RVs extracted from CCF with telluric correction applied. | ``Public``     |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | ``SKYSUB``                | ``"POSTDRS_SKYSUB_A"``    | Standard DRS pipeline processing, RVs extracted from CCF with sky subtraction applied.     | ``Public``     |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | ``PUBLICATION``           | ``"PUB"``                 | RVs imported from publications.                                                            | ``Public``     |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | ``SBART``                 | ``"SBART"``               | RVs extracted using the SBART method.                                                      | ``Private``    |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
            | ``LBL``                   | ``"LBL"``                 | RVs extracted using the LBL method.                                                        | ``Private``    |
            +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+

        :param target: The target to retrieve data from.
        :type target: str
        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param rv_sources: List of Source enum values to filter the radial velocity data by their source
        :type rv_sources: Optional[list[Source]]
        :param sorted_by_instrument: Application of the instrument sorting
        :type sorted_by_instrument: Optional[bool]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting spectroscopy timeseries for a target
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                target_to_search = "C15-0734"
                timeseries = Spectroscopy.get_timeseries(target=target_to_search)
        
        .. dropdown:: Getting spectroscopy timeseries for a target with filters applied
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
            
                target_to_search = "HR3259"
                filters_to_use = dict(
                    instrument_name=dict(contains=['HARPS']),
                    rjd=dict(min=58000, max=59000)
                )
                
                timeseries = Spectroscopy.get_timeseries(target=target_to_search, filters=filters_to_use)
        
        .. dropdown:: Getting spectroscopy timeseries for a target with results sorted by <instrument>/<drs>/<instrument_mode>
            :color: success
            :icon: code-square
            
            .. code-block:: python 
            
                from dace_query.spectroscopy import Spectroscopy
                    target_to_search = "C15-0734"
                    timeseries = Spectroscopy.get_timeseries(target=target_to_search, sorted_by_instrument=True)
        
        .. dropdown:: Getting timeseries with from a specific radial velocity source (ex: only telluric corrected data)
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                    timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Spectroscopy.Source.TELLURIC_CORRECTION])
                

        .. dropdown:: Filtering spectroscopy timeseries by multiple radial velocity sources (ex: SKYSUB and TELLURIC_CORRECTION)
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                    timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Spectroscopy.Source.SKYSUB, Spectroscopy.Source.TELLURIC_CORRECTION])
                

        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}
        
        # Allows to filter the source product file extensions based on the Source enum
        if rv_sources:
            rv_sources = rv_sources if isinstance(rv_sources, list) else [rv_sources]
            
            if not all(isinstance(pt, Source) for pt in rv_sources):
                raise ValueError("rv_sources must be a list of Source enum values, ex: [Source.STANDARD_PROCESSING, Source.PUBLICATION]")
                
            filters["source_product_file_ext"] = {"equals": [pt.value for pt in rv_sources]}
        
        spectroscopy_data = self.dace.request_get(
            api_name=self.__SPECTROSCOPY_API,
            endpoint=f'target/{target}/timeseries/radial-velocities',
            params={
                'limit': str(limit),
                'filters': json.dumps(filters),
                'sort': json.dumps(sort)
            }
        )
        
        if sorted_by_instrument:
            transformed_data = self.dace.transform_to_format(spectroscopy_data, output_format='numpy')
            return self.dace.order_spectroscopy_data_by_instruments(transformed_data)
        else:
            return self.dace.transform_to_format(spectroscopy_data, output_format=output_format)



    def browse_products(self,
                filters: dict,
                file_type: str = None,
                output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        List the filenames of all available data products for observations (raw frames) matching the specified filters.
        
        This method mirrors the signature of :meth:`download`, making it ideal for previewing available data products 
        before performing any actual downloads. Use it to examine what files would be retrieved based on your 
        filters, file_type, and aperture settings.
        
        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the spectroscopy database.
        **Filters** can be applied to the query via named arguments (see :doc:`query_options`).
        
        .. dropdown:: Setting filters
            :color: primary
            :icon: code-square
        
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}

        
        :param filters: Filters to apply to the query
        :type filters: dict
        :param file_type: The type of files to download
        :type file_type: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict


        .. dropdown:: Listing all available products for a given target name
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                values = Spectroscopy.browse_products(filters={'target_name':{'equal': [target_name]}})
                

        .. dropdown:: Listing all available products using a list of raw frames
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy

                # Let's say we want to get a list of all observations (raw frames) for 'HR3259' on '2018-11-03'
                raw_frame_filters = dict(target_name=dict(equal=['HR3259']), date_night=dict(equal=['2018-11-03']))
                raw_frames = Spectroscopy.query_database(filters=raw_frame_filters, output_format='dict')

                # Get the unique ids of those raw frames
                spectrum_ids = raw_frames.get('spectrum_id')

                # Pass the list of ids to browse_products to get the list of available products for those spectra
                if spectrum_ids:
                    products = Spectroscopy.browse_products(filters={'spectrum_id':{'equal':spectrum_ids}}, output_format='dict')
        

        .. dropdown:: Listing all available ``CCF_A`` for a given target name
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                values = Spectroscopy.browse_products(filters={'target_name':{'equal': [target_name]}}, file_type='CCF_A')
                
        """
        if filters is None:
            filters = {}
            
        # Add support for legacy file type abbreviations (s1d, s2d, ccf, all)
        corrected_file_type = _adapt_legacy_file_type(file_type)
            
        products = self.dace.request_post(
            api_name=self.__SPECTROSCOPY_API,
            endpoint='download/browse',
            data=json.dumps({
                'fileType': corrected_file_type,
                'filters': filters
                })
        )
        return self.dace.transform_to_format(products, output_format=output_format)

Spectroscopy: SpectroscopyClass = SpectroscopyClass()
"""
This is a singleton instance of the :class:`SpectroscopyClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
"""