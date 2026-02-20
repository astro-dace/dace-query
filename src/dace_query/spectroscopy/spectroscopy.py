from __future__ import annotations

from enum import Enum
import json
import logging
import re
import warnings

from typing import Union, Optional
from io import BytesIO
from astropy.coordinates import SkyCoord, Angle
from astropy.table import Table
from astropy.io import fits
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
    Enumeration of the different sources of radial velocity (RV) data.
    Used to filter RV time series data based on their provenance and/or extraction pipeline.

    A *source* is a label describing how an RV time series was produced (or ingested).

    For RVs produced by a cross-correlation function (CCF) based DRS pipeline, multiple RV series may exist for the same observations depending on
    the processing variant (for example ``standard``, ``telluric-corrected``, or ``sky-subtracted`` CCF products).

    Other sources may correspond to alternative RV extraction pipelines, RVs resulting from a specific post-processing (i.e. SBART), 
    or to RVs imported from an alternative source such as a publication.

    By default, :meth:`SpectroscopyClass.get_timeseries` returns RVs from the ``STANDARD_PROCESSING`` and ``PUBLICATION`` sources, but you can specify
    which sources to include or exclude using the ``rv_sources`` argument.

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
        | ``STANDARD_PROCESSING``   | ``"POSTDRS_A"``           | Standard DRS pipeline processing, RVs extracted from CCF. **(default)**                    | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``TELLURIC_CORRECTION``   | ``"POSTDRS_TELL_CORR_A"`` | Standard DRS pipeline processing, RVs extracted from CCF with telluric correction applied. | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``SKYSUB``                | ``"POSTDRS_SKYSUB_A"``    | Standard DRS pipeline processing, RVs extracted from CCF with sky subtraction applied.     | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``PUBLICATION``           | ``"PUB"``                 | RVs imported from publications. **(default)**                                              | ``Public``     |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``SBART``                 | ``"SBART"``               | RVs extracted using the SBART method.                                                      | ``Private``    |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        | ``LBL``                   | ``"LBL"``                 | RVs extracted using the LBL method.                                                        | ``Private``    |
        +---------------------------+---------------------------+--------------------------------------------------------------------------------------------+----------------+
        
    .. dropdown:: Filtering radial velocity time series data by source
        :color: info
        :icon: list-unordered
    
        **Getting only telluric corrected radial velocity data:**
        
        .. code-block:: python

            from dace_query.spectroscopy import Spectroscopy, Source
            timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Source.TELLURIC_CORRECTION])
                
        **Getting standard and publication radial velocity data:**
        
        .. code-block:: python
        
            from dace_query.spectroscopy import Spectroscopy, Source
            timeseries = Spectroscopy.get_timeseries('HR3259', rv_sources=[Source.STANDARD_PROCESSING, Source.PUBLICATION])
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


    def _fetch_drs_ids(self, drs_version: Union[str, list[str]]) -> list[str]:
        """
        Return the DRS IDs that match a DRS version string.

        The input can be written in several common formats, for example:

        - ``DRS-X.Y.Z`` (e.g. ``DRS-3.3.10``)
        - ``X.Y.Z`` (e.g. ``3.3.10``)
        - ``DRS-X.Y.Z-EXTRACTION_METHOD`` (e.g. ``DRS-3.3.10-SBART`` or ``DRS-3.3.10-CCF``)
        - Any other variant that still includes the major, minor, and patch numbers (e.g. ``drs.3.3.10`` or ``drs-3-3-10``)
        """
        if isinstance(drs_version, str):
            drs_version = [drs_version]
        elif isinstance(drs_version, list):
            drs_version = drs_version
        else:
            raise ValueError("drs_version must be a string or a list of strings")
                
        filters_for_drs = {'drs_version': {'equal': drs_version}}
                        
        drs = self.dace.request_get(
            api_name=self.__SPECTROSCOPY_API,
            endpoint='drs',
            params={
                'filters': json.dumps(filters_for_drs)
            }
        )
        
        drs = self.dace.transform_to_format(drs, output_format='dict')
        
        return drs.get('drs_id', [])

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
                 drs_version: Optional[Union[str, list[str]]] = None,
                 compressed: Optional[bool] = False,
                 output_directory: Optional[str] = None,
                 output_filename: Optional[str] = None):
        """
        Download reduced products (``CCF``, ``S1D``, ``S2D``, etc.) for observations (raw frames) matching the specified filters.

        **Before downloading:** you can use :meth:`browse_products` with identical parameters to preview 
        what files would be downloaded. This is particularly useful for large data sets.

        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the spectroscopy database.
        
        **Filters** can be applied to the query via the ``filters`` argument (see :doc:`query_options`).
        You can filter on any field available for a raw frame in :meth:`query_database` (e.g. ``target_name``, ``spectrum_id``, ``date_night``, ``file_rootname``, ...).
        
        .. dropdown:: Setting filters
            :color: primary
            :icon: filter
        
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}
                
        .. dropdown:: Filtering by DRS version
                :color: info
                :icon: filter

                You can restrict which products are returned by specifying the ``drs_version`` argument.
                
                +------------------------------------+--------------------------------------------------------------------------+
                | Value                              | Description                                                              |
                +====================================+==========================================================================+
                | ``None``                           | Do not filter by DRS version (default)                                   |
                +------------------------------------+--------------------------------------------------------------------------+
                | ``'latest'``                       | Select the latest available DRS version                                  |
                +------------------------------------+--------------------------------------------------------------------------+
                | ``'DRS-<major>.<minor>.<patch>'``  | Select a specific DRS version                                            |
                |                                    | (e.g. ``'DRS-3.3.10'`` or ``'3.3.10'`` or ``'DRS-3.3.10-CCF'``)          |
                +------------------------------------+--------------------------------------------------------------------------+


                Example:

                .. code-block:: python

                        from dace_query.spectroscopy import Spectroscopy

                        filters = {'target_name': {'equal': ['TOI178']}}
                        
                        # Download CCFs for the latest DRS version available
                        Spectroscopy.download(filters=filters, file_type='ccf', drs_version='latest')
                        
                        # Download S1D products for a specific DRS version (e.g. DRS-3.3.10)
                        Spectroscopy.download(filters=filters, file_type='s1d', drs_version='DRS-3.3.10')
                        
                        # Download S2D products for a specific DRS version with a specifiic extraction method (e.g. DRS-3.3.10-CCF or DRS-3.3.10-SBART)
                        Spectroscopy.download(filters=filters, file_type='s2d', drs_version='DRS-3.3.10-CCF')

        .. dropdown:: Filtering file types
            :color: info
            :icon: list-unordered

            You can specify the type of files to download using the ``file_type`` argument.

            Available values:

            +----------------------+-----------------------------------+
            | Value                | Corresponding file types          |
            +======================+===================================+
            | ``'s1d'``            | ``S1D_A``, ``S1D_B``              |
            +----------------------+-----------------------------------+
            | ``'s2d'``            | ``S2D_A``, ``S2D_B``              |
            +----------------------+-----------------------------------+
            | ``'ccf'``            | ``CCF_A``, ``CCF_B``              |
            +----------------------+-----------------------------------+
            | ``'all'`` or ``None``| All file types (default)          |
            +----------------------+-----------------------------------+

            You can also pass exact file types (e.g. ``'S1D_A'`` or ``'CCF_B'``)
            
            or a list of exact file types (e.g. ``['S1D_A', 'S1D_B', 'CCF_B']``) to download specific products.

            To check which file types are available for your filters, you may use :meth:`browse_products`.

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
        :param file_type: The type of files to download (see "Filtering file types")
        :type file_type: Optional[str]
        :param drs_version: The DRS version of the products to browse (e.g. ``'latest'`` or specific version in the format ``'DRS-<major>.<minor>.<patch>-<rv_extraction_method>'``)
        :type drs_version: Optional[Union[str, list[str]]]
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

        .. dropdown:: Downloading all ``ccf`` files for a given target name and the latest DRS version available
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                filters = {'target_name':{'equal': [target_name]}}
                Spectroscopy.download(file_type='ccf', filters=filters, drs_version='latest')
                
                
        .. dropdown:: Downloading all ``s1d`` files for a given target name and a specific DRS version (e.g. ``DRS-3.3.10``)
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                filters = {'target_name':{'equal': [target_name]}}
                Spectroscopy.download(file_type='s1d', filters=filters, drs_version='DRS-3.3.10')
        """
        if filters is None:
            filters = {}
                        
        # Add support for legacy file type abbreviations (s1d, s2d, ccf, all)
        corrected_file_type = _adapt_legacy_file_type(file_type)
                        
        drs_ids = []
        endpoint = 'download'
        
        # If the user provided a specific DRS version...
        if drs_version is not None:
            # Requested the latest DRS version available
            if drs_version == 'latest':
                endpoint = 'download/latest'
            # Requested a specific DRS version
            else:
                drs_ids = self._fetch_drs_ids(drs_version)
                        
        response = self.dace.request_post(
            api_name=self.__SPECTROSCOPY_API,
            endpoint=endpoint,
            data=json.dumps({
                'fileType': corrected_file_type,
                'filters': filters,
                'drsIds': drs_ids
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
                       rv_sources: Optional[list[Source]] = [Source.STANDARD_PROCESSING, Source.PUBLICATION],
                       drs_version: Optional[Union[str, list[str]]] = None,
                       sorted_by_instrument: Optional[bool] = True,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Retrieve the spectroscopy time series data for a specified target in the chosen format.

        Filters can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).
        
        Using ``sorted_by_instrument=True`` will sort the results by ``instrument → DRS version → instrument mode``
        and return a nested dictionary structure as shown in the sample output below.
        
        **Note :** when using ``sorted_by_instrument=True``, the ``output_format`` argument is ignored.
        
        
        .. dropdown:: Sample output with ``sorted_by_instrument=True``
            :color: info
            :icon: info
            
            .. code-block:: python
            
                    {
                        'HARPS15': {
                            'DRS-3.3.6-CCF': {
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
                            'DRS-3.3.10-CCF': {
                                ...
                            }
                            'DRS-3.3.10-SBART': {
                                ...
                            }
                        },
                        'ESPRESSO19': {
                            ...
                        }
                    }


        .. dropdown:: Selecting radial velocity sources
            :color: info
            :icon: info

            The ``rv_sources`` argument allows to filter the radial velocity data based on their provenance (e.g. standard DRS processing, specific post-processing, or publications).
            See the :class:`Source` enum for available options and usage examples.
            
            By default, this method returns RVs from ``Source.STANDARD_PROCESSING`` (standard DRS / CCF)
            and ``Source.PUBLICATION``.
            
            Some DRS or postprocesses may be marked as ``Private`` if they are not publicly available.
            To access private data, ensure you have the necessary permissions and `authentication <dace_introduction.html#authentication>`_.
            
            .. dropdown:: Tips for working with the output when ``sorted_by_instrument=True``
                :color: success
                :icon: info

                When ``sorted_by_instrument=True``, the output is a nested dictionary grouped by:
                
                    ``instrument → DRS version → instrument mode``.

                If you request multiple RV sources that come from the **same DRS** (same instrument/DRS/mode), they are returned
                together in the **same series**.

                For example, if you include both ``Source.STANDARD_PROCESSING`` and ``Source.TELLURIC_CORRECTION``, you will get
                two RV points per observation in the same series (one telluric-corrected and one not), under the same instrument/DRS/mode key.
                
                This might not be desirable if you want to keep telluric-corrected and non-telluric-corrected RVs separate, in which case you can either:
                
                - Make two separate calls to :meth:`get_timeseries`, one for each source, to get separate series for each source while keeping the grouping by instrument/DRS/mode.
                - Set ``sorted_by_instrument=False`` to get a flat structure where each row corresponds to a single point (which can be further filtered using pandas)
                

        .. dropdown:: Filtering by DRS version
            :color: info
            :icon: filter

            You can further restrict which series are returned by specifying the ``drs_version`` argument.            

            +------------------------------------+--------------------------------------------------------------------------+
            | Value                              | Description                                                              |
            +====================================+==========================================================================+
            | ``None``                           | Do not filter by DRS version (default)                                   |
            +------------------------------------+--------------------------------------------------------------------------+
            | ``'latest'``                       | Select the latest available DRS version per instrument                   |
            +------------------------------------+--------------------------------------------------------------------------+
            | ``'DRS-<major>.<minor>.<patch>'``  | Select a specific DRS version                                            |
            |                                    | (e.g. ``'DRS-3.3.10'`` or ``'3.3.10'`` or ``'DRS-3.3.10-CCF'``)          |
            +------------------------------------+--------------------------------------------------------------------------+

            Example:

            .. code-block:: python

                    from dace_query.spectroscopy import Spectroscopy
                    
                    # Get timeseries for the latest DRS version available per instrument
                    timeseries = Spectroscopy.get_timeseries(target='HD69830', drs_version='latest')
                    
                    # Ge timeseries for a specific DRS version (e.g. DRS-3.3.10)
                    timeseries = Spectroscopy.get_timeseries(target='HD69830', drs_version='DRS-3.3.10')
                    
                    # Get timeseries for a specific DRS version with a specifiic extraction method (e.g. DRS-3.3.10-CCF or DRS-3.3.10-SBART)
                    # Make sure to specify the source (by default we only include standard processing and publications)
                    timeseries = Spectroscopy.get_timeseries(target='HD69830', rv_sources=[Source.SBART], drs_version='DRS-3.3.10-SBART')


            If you set both ``rv_sources`` and ``drs_version``, we apply **both** filters.
            This means you only get radial-velocity time series that match the selected sources
            **and** belong to the selected DRS version.

            If that DRS version does not exist for the selected source(s) (for example because it corresponds
            to a different extraction method / pipeline), then there is no overlap and you will get **no results**.
            
            Pick a DRS version that matches the RV sources you selected, for example:
            
            .. code-block:: python
                
                from dace_query.spectroscopy import Spectroscopy, Source
                
                # Yields no results as SBART is not selected in rv_sources by default
                timeseries = Spectroscopy.get_timeseries(
                    target='HR3259',
                    drs_version='DRS-3.3.10-SBART' 
                )
                
                timeseries = Spectroscopy.get_timeseries(
                    target='HR3259',
                    rv_sources=[Source.SBART, Source.STANDARD_PROCESSING], # Get both standard and SBART radial velocities
                    drs_version='DRS-3.3.10-SBART'                         # Returns only SBART series from DRS-3.3.10
                )
                
                timeseries = Spectroscopy.get_timeseries(
                    target='HR3259',
                    rv_sources=[Source.SBART, Source.STANDARD_PROCESSING], # Get both standard and SBART radial velocities
                    drs_version='DRS-3.3.10'                               # Returns SBART + standard series from DRS-3.3.10 (if available)
                )
                
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
        :param drs_version: The DRS version to filter the data (e.g. ``'latest'`` or specific version in the format ``'DRS-<major>.<minor>.<patch>-<rv_extraction_method>'``)
        :type drs_version: Optional[Union[str, list[str]]]
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
            
        # Allow to filter by DRS version if the user provided a drs_version argument
        if drs_version is not None:
            if drs_version == 'latest':
                filters['is_latest_drs'] = {'is': True}
            else:
                drs_ids = self._fetch_drs_ids(drs_version)
                if drs_ids:
                    filters['drs_id'] = {'equal': drs_ids}
                else:
                    self.log.warning(f"No DRS found matching the provided drs_version '{drs_version}'.")
                    return {}
        
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
                drs_version: Optional[Union[str, list[str]]] = None,
                output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        List the filenames of all available data products for observations (raw frames) matching the specified filters.
        
        This method mirrors the signature of :meth:`download`, making it ideal for previewing available data products 
        before performing any actual downloads. Use it to examine what files would be retrieved based on your 
        ``filters``, ``file_type``, and ``drs_version``
        
        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the spectroscopy database.
        
        **Filters** can be applied to the query via the ``filters`` argument (see :doc:`query_options`).
        You can filter on any field available for a raw frame in :meth:`query_database` (e.g. ``target_name``, ``spectrum_id``, ``date_night``, ``file_rootname``, ...).
        
        .. dropdown:: Setting filters
            :color: primary
            :icon: filter
        
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}
                
        .. dropdown:: Filtering by DRS version
                :color: info
                :icon: filter

                You can restrict which products are returned by specifying the ``drs_version`` argument.

                +------------------------------------+--------------------------------------------------------------------------+
                | Value                              | Description                                                              |
                +====================================+==========================================================================+
                | ``None``                           | Do not filter by DRS version (default)                                   |
                +------------------------------------+--------------------------------------------------------------------------+
                | ``'latest'``                       | Select the latest available DRS version                                  |
                +------------------------------------+--------------------------------------------------------------------------+
                | ``'DRS-<major>.<minor>.<patch>'``  | Select a specific DRS version                                            |
                |                                    | (e.g. ``'DRS-3.3.10'`` or ``'3.3.10'`` or ``'DRS-3.3.10-CCF'``)          |
                +------------------------------------+--------------------------------------------------------------------------+


                Example:

                .. code-block:: python

                        from dace_query.spectroscopy import Spectroscopy

                        filters = {'target_name': {'equal': ['TOI178']}}
                        
                        # Download CCFs for the latest DRS version available
                        Spectroscopy.download(filters=filters, file_type='ccf', drs_version='latest')
                        
                        # Download S1D products for a specific DRS version (e.g. DRS-3.3.10)
                        Spectroscopy.download(filters=filters, file_type='s1d', drs_version='DRS-3.3.10')
                        
                        # Download S2D products for a specific DRS version with a specifiic extraction method (e.g. DRS-3.3.10-CCF or DRS-3.3.10-SBART)
                        Spectroscopy.download(filters=filters, file_type='s2d', drs_version='DRS-3.3.10-CCF')

        .. dropdown:: Filtering file types
            :color: info
            :icon: list-unordered

            You can specify the type of files to list using the ``file_type`` argument.

            Available values:

            +----------------------+-----------------------------------+
            | Value                | Corresponding file types          |
            +======================+===================================+
            | ``'s1d'``            | ``S1D_A``, ``S1D_B``              |
            +----------------------+-----------------------------------+
            | ``'s2d'``            | ``S2D_A``, ``S2D_B``              |
            +----------------------+-----------------------------------+
            | ``'ccf'``            | ``CCF_A``, ``CCF_B``              |
            +----------------------+-----------------------------------+
            | ``'all'`` or ``None``| All file types (default)          |
            +----------------------+-----------------------------------+

            You can also pass exact file types (e.g. ``'S1D_A'`` or ``'CCF_B'``)
            
            or a list of exact file types (e.g. ``['S1D_A', 'S1D_B', 'CCF_B']``) to download specific products.
            
            
        :param filters: Filters to apply to the query
        :type filters: dict
        :param file_type: The type of files to download (see "Filtering file types")
        :type file_type: str
        :param drs_version: The DRS version of the products to browse (e.g. ``'latest'`` or specific version in the format ``'DRS-<major>.<minor>.<patch>-<rv_extraction_method>'``)
        :type drs_version: Optional[Union[str, list[str]]]
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
                filters = {'target_name':{'equal': [target_name]}}
                values = Spectroscopy.browse_products(filters=filters, file_type='CCF_A')


        .. dropdown:: Listing all ``ccf`` files for a given target name and the latest DRS version available
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                filters = {'target_name':{'equal': [target_name]}}
                Spectroscopy.browse_products(filters=filters, file_type='ccf', drs_version='latest')
                
                
        .. dropdown:: Listing all ``s1d`` files for a given target name and a specific DRS version (e.g. ``DRS-3.3.10``)
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from dace_query.spectroscopy import Spectroscopy
                
                target_name = 'TOI178'
                filters = {'target_name':{'equal': [target_name]}}
                Spectroscopy.browse_products(filters=filters, file_type='s1d', drs_version='DRS-3.3.10')
        """
        if filters is None:
            filters = {}
            
        # Add support for legacy file type abbreviations (s1d, s2d, ccf, all)
        corrected_file_type = _adapt_legacy_file_type(file_type)
        
        drs_ids = []
        endpoint = 'download/browse'
        
        # If the user provided a specific DRS version...
        if drs_version is not None:
            # Requested the latest DRS version available
            if drs_version == 'latest':
                endpoint = 'download/browse/latest'
            # Requested a specific DRS version
            else:
                drs_ids = self._fetch_drs_ids(drs_version)
            
        products = self.dace.request_post(
            api_name=self.__SPECTROSCOPY_API,
            endpoint=endpoint,
            data=json.dumps({
                'fileType': corrected_file_type,
                'filters': filters,
                'drsIds': drs_ids
                })
        )
        return self.dace.transform_to_format(products, output_format=output_format)



    def get_guiding_frame(self, spectrum_id: int) -> fits.HDUList:
        """
        Retrieve the guiding frame associated with a given raw frame (using the raw frame's unique identifier ``spectrum_id`` to find it).
        
        The guiding frame frame is returned as an ``astropy.io.fits.HDUList`` object, which can be manipulated using the astropy library.
        As such, actual frame data and headers are provided by the API, just like when opening a fits file using astropy's ``fits.open()`` method. 
        
        You can for example access the data of the guiding frame using ``guiding_frame[0].data`` and its header using ``guiding_frame[0].header``.

        :param spectrum_id: The unique id of a raw frame to retrieve the guiding frame for
        :type spectrum_id: int
        :return: The guiding frame as an astropy.io.fits.HDUList object, or None if no guiding frame is available
        :rtype: fits.HDUList or None

        .. dropdown:: Getting the guiding frame for a specific spectrum ID
            :color: success
            :icon: code-square

            .. code-block:: python

                from dace_query.spectroscopy import Spectroscopy
                
                spectrum_id_to_search = 6
                
                # This is equivalent to opening the fits file of the guiding frame directly 
                # and reading its data using fits.open() from astropy.io
                guiding_frame = Spectroscopy.get_guiding_frame(spectrum_id=spectrum_id_to_search)
                
                
        .. dropdown:: Getting searching for an observation using ``query_database`` and getting its guiding frame
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from matplotlib import pyplot as plt
                from dace_query.spectroscopy import Spectroscopy

                # Set the raw frame filters and fetch the raw frame using query_database
                file_rootname = 'ESPRE.2018-07-08T08:02:09.755.fits'
                raw_frame = Spectroscopy.query_database(filters={"file_rootname":{"equals":[file_rootname]}})
                
                # Extract the spectrum_id of the first raw frame matching the filters 
                # (there should only be one in this case since we filtered by file name)
                spectrum_id = raw_frame.get('spectrum_id')[0]

                # This is equivalent to opening the fits file of the guiding frame directly 
                # and reading its data using fits.open() from astropy.io
                guiding_frame = Spectroscopy.get_guiding_frame(spectrum_id)
                
        .. dropdown:: Displaying the guiding frame using matplotlib
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from matplotlib import pyplot as plt
                from dace_query.spectroscopy import Spectroscopy
            
                # This is equivalent to opening the fits file of the guiding frame directly 
                # and reading its data using fits.open() from astropy.io
                guiding_frame = Spectroscopy.get_guiding_frame(spectrum_id=6)
            
                # Only plot data if a guiding frame was successfully retrieved
                if guiding_frame is not None:
                    
                    # Extract the data from the first HDU (Header Data Unit) of the fits file
                    data = guiding_frame[0].data

                    # Display the image using matplotlib
                    plt.imshow(data, origin='lower', cmap='viridis')
                    plt.colorbar()
                    plt.show()
                    
        .. dropdown:: Displaying the guiding frame of a perticular point from ``get_timeseries`` using matplotlib
            :color: success
            :icon: code-square
            
            .. code-block:: python
            
                from matplotlib import pyplot as plt
                from dace_query.spectroscopy import Spectroscopy
                
                # Get the spectroscopy timeseries for a target
                target = 'HR3259'

                # Build the filters to only include points from a specific instrument group (e.g. ESPRESSO)
                instrument_group_filters = { "instrument_group" : { "equals" : ["ESPRESSO"] } }
                
                # Get the timeseries for that target with the instrument group filters applied
                timeseries = Spectroscopy.get_timeseries(target=target, filters=instrument_group_filters, sorted_by_instrument=True)

                # Extract the spectrum_id of a particular point in the timeseries (for example the first point of the first instrument/DRS/mode available)
                first_instrument = next(iter(timeseries))
                first_drs = next(iter(timeseries[first_instrument]))
                first_ins_mode = next(iter(timeseries[first_instrument][first_drs]))
                
                # For this example, we simply get the spectrum_id of the first point in the timeseries, 
                # but you can of course select any point you want based on the available metadata (e.g. rjd, rv, etc.) 
                # and get its spectrum_id to retrieve the corresponding guiding frame
                spectrum_id = timeseries[first_instrument][first_drs][first_ins_mode]['spectrum_id'][0]

                # This is equivalent to opening the fits file of the guiding frame directly 
                # and reading its data using fits.open() from astropy.io
                guiding_frame = Spectroscopy.get_guiding_frame(spectrum_id=spectrum_id)

                # Only plot data if a guiding frame was successfully retrieved
                if guiding_frame is not None:

                    # Extract the data from the first HDU (Header Data Unit) of the fits file
                    data = guiding_frame[0].data

                    # Display the image using matplotlib
                    plt.imshow(data, origin='lower', cmap='viridis')
                    plt.colorbar()
                    plt.show()
        """
        response = self.dace.request_get(
            api_name=self.__SPECTROSCOPY_API,
            endpoint=f'guiding/{spectrum_id}',
            raw_response=True
        )
        
        if not response:
            self.log.warning(f"No guiding frame available for spectrum_id {spectrum_id}.")
            return None
        
        
        # Response contains the binary data of the guiding frame fits file, we can read it using astropy.io.fits
        try:
            hdul = fits.open(BytesIO(response))
        except Exception as e:
            self.log.error(f"Failed to read guiding frame for spectrum_id {spectrum_id}: {e}")
            return None
        
        return hdul
        
    
Spectroscopy: SpectroscopyClass = SpectroscopyClass()
"""
This is a singleton instance of the :class:`SpectroscopyClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
"""