from __future__ import annotations

import json
import logging
from typing import Union, Optional
import warnings

from astropy.coordinates import SkyCoord, Angle
from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass
from dace_query.dace import NoDataException

CHEOPS_DEFAULT_LIMIT = 10000


class CheopsClass:
    """
    The cheops class.
    Use to retrieve data from the cheops module.

    .. tip::
    
        A cheops instance is already provided, to use it :
        
        .. code-block:: python
        
            from dace_query.cheops import Cheops
    """
    __ACCEPTED_FILE_TYPES = [
        'lightcurves',
        'images',
        'reports',
        'full',
        'sub',
        'all',
        'EXT_PRE_StarCatalogue',
        'MCO_REP_BadPixelMapFullArray',
        'MCO_REP_BadPixelMapSubArray',
        'MCO_REP_DarkFrameFullArray',
        'MCO_REP_DarkFrameSubArray',
        'PIP_COR_PixelFlagMapSubArray',
        'PIP_REP_DarkColumns',
        'SCI_CAL_SubArray',
        'SCI_COR_Lightcurve',
        'SCI_COR_SubArray',
        'SCI_RAW_Attitude',
        'SCI_RAW_Centroid',
        'SCI_RAW_EventReport',
        'SCI_RAW_FullArray',
        'SCI_RAW_HkAsy30759',
        'SCI_RAW_HkAsy30767',
        'SCI_RAW_HkCe',
        'SCI_RAW_HkCentroid',
        'SCI_RAW_HkDefault',
        'SCI_RAW_HkExtended',
        'SCI_RAW_HkIaswPar',
        'SCI_RAW_HkIfsw',
        'SCI_RAW_HkOperationParameter',
        'SCI_RAW_Imagette',
        'SCI_RAW_SubArray',
        'log',
        'mp4',
        'pdf']

    __ACCEPTED_CATALOGS = ['planet', 'stellar']

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable cheops object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]


        .. code-block:: python
        
            from dace_query.cheops import CheopsClass
            cheops_instance = CheopsClass()

        """
        self.__CHEOPS_API = 'cheops-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"cheops-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self,
                       limit: Optional[int] = CHEOPS_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the cheops database to retrieve available visits in the chosen format.

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


        .. dropdown:: List all available CHEOPS visits
            :color: success
            :icon: code-square
            
            .. code-block:: python
        
                from dace_query.cheops import Cheops
                values = Cheops.query_database()
        """

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__CHEOPS_API,
                endpoint='search',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }
            ), output_format=output_format)

    def query_catalog(self,
                      catalog: str,
                      limit: Optional[int] = CHEOPS_DEFAULT_LIMIT,
                      filters: Optional[dict] = None,
                      sort: Optional[dict] = None,
                      output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the cheops, either stellar or planet, catalogs.

        Available catalogs are [ 'planet', 'stellar' ].

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param catalog: The catalog name
        :type catalog: str
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

        .. dropdown:: Getting the planet catalog
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.cheops import Cheops
                catalog_to_search = 'planet'
                values = Cheops.query_catalog(catalog_to_search)
        """

        if catalog not in self.__ACCEPTED_CATALOGS:
            raise ValueError('catalog must be one of these values : ' + ','.join(self.__ACCEPTED_CATALOGS))

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__CHEOPS_API,
                endpoint=f'catalog/{catalog}',
                params={
                    'limit': str(limit),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }), output_format=output_format)

    def query_region(self,
                     sky_coord: SkyCoord,
                     angle: Angle,
                     limit: Optional[int] = CHEOPS_DEFAULT_LIMIT,
                     filters: Optional[dict] = None,
                     output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query a region, based on SkyCoord and Angle objects, in the Cheops database and retrieve data in the chosen
        format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

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

        .. dropdown:: Finding visits using a cone search
            :color: success
            :icon: code-square
            
            .. code-block:: python
        
                from dace_query.cheops import Cheops
                from astropy.coordinates import SkyCoord, Angle
                sky_coord, angle = SkyCoord("22h23m29s", "+32d27m34s", frame='icrs'), Angle('0.045d')
                values = Cheops.query_region(sky_coord=sky_coord, angle=angle)

        """

        coordinate_filter_dict = self.dace.transform_coordinates_to_dict(sky_coord, angle)
        filters_with_coordinates = {}
        if filters is not None:
            filters_with_coordinates.update(filters)
        filters_with_coordinates.update(coordinate_filter_dict)
        return self.query_database(limit=limit, filters=filters_with_coordinates, output_format=output_format)

    def get_lightcurve(self,
                       target: str,
                       aperture: Optional[str] = 'default',
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Get the photometry data (from Cheops) in the chosen format for a specified target.

        Aperture types available are : ``'default'``, ``'optimal'``, ``'rinf'`` and ``'rsup'``

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        :param target: The target to retrieve light curve from
        :type target: str
        :param aperture: Aperture type
        :type aperture: Optional[str]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: The desired data in the chosen output format
        :type output_format: Optional[str]
        :return: The desired data in the chosen format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting all available photometry data for a specific target
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.cheops import Cheops
                values = Cheops.get_lightcurve('WASP-8')
        """
        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        # a = 'photometry/' + target + '?aperture=' + aperture + '&filters=' +
        # self.dace.transform_dict_to_encoded_json(filters) + '&sort=' + self.dace.transform_dict_to_encoded_json(sort)

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__CHEOPS_API,
                endpoint=f'photometry/{target}',
                params={
                    'aperture': str(aperture),
                    'filters': json.dumps(filters),
                    'sort': json.dumps(sort)
                }), output_format=output_format
        )

    def download(self,
                 filters: dict,
                 file_type: str = 'all',
                 aperture: Optional[str] = None,
                 compressed: Optional[bool] = True,
                 output_directory: Optional[str] = None,
                 output_filename: Optional[str] = None) -> None:
        """
        Download CHEOPS data products (`.fits`, `.pdf`, etc.) for visits matching the specified filters.

        **Before downloading:** Use :meth:`browse_products` with identical parameters to preview 
        what files would be downloaded. This is particularly useful for large data sets.
    
        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the CHEOPS database.
        **Filters** can be applied to the query via named arguments (see :doc:`query_options`).
        
        .. dropdown:: Setting filters
            :color: primary
            :icon: code-square
        
            .. code-block:: python
            
                # Filtering using file_key
                file_key = 'CH_PR100018_TG027204_V0200'
                filters: dict = {'file_key':{'equal': [file_key]}}
            
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}


        **File types** can be specified in two ways:

        .. dropdown:: General categories
            :color: info
            :icon: list-unordered
    
            * ``lightcurves``
            * ``images``
            * ``reports``
            * ``full``
            * ``sub``
            * ``all``


        .. dropdown:: Specific CHEOPS product identifiers
            :color: info
            :icon: list-unordered

            * ``EXT_PRE_StarCatalogue``
            * ``MCO_REP_BadPixelMapFullArray``
            * ``MCO_REP_BadPixelMapSubArray``
            * ``MCO_REP_DarkFrameFullArray``
            * ``MCO_REP_DarkFrameSubArray``
            * ``PIP_COR_PixelFlagMapSubArray``
            * ``PIP_REP_DarkColumns``
            * ``SCI_CAL_SubArray``
            * ``SCI_COR_Lightcurve``
            * ``SCI_COR_SubArray``
            * ``SCI_RAW_FullArray``
            * ``SCI_RAW_Imagette``
            * ``SCI_RAW_SubArray``
            * ``SCI_RAW_Attitude``
            * ``SCI_RAW_Centroid``
            * ``SCI_RAW_EventReport``
            * ``SCI_RAW_HkAsy30759``
            * ``SCI_RAW_HkAsy30767``
            * ``SCI_RAW_HkCe``
            * ``SCI_RAW_HkCentroid``
            * ``SCI_RAW_HkDefault``
            * ``SCI_RAW_HkExtended``
            * ``SCI_RAW_HkIaswPar``
            * ``SCI_RAW_HkIfsw``
            * ``SCI_RAW_HkOperationParameter``
            * ``log``
            * ``mp4``
            * ``pdf``
        
        Files are sent in different formats based on the number of files to download:
    
        - **Single file**: native format (``.fits``, ``.pdf``, ``.mp4``, etc.)
        - **Multiple files**: archive (``.tar`` or ``.tar.gz``)
        
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
        
        **Aperture** can be used to further filter products.
        It is useful in the case where we need to download a single specific ``lightcurves`` or ``mp4`` data product.
        Setting the aperture on other file types is not supported and will raise an error.
        
        Aperture types available are : ``'default'``, ``'optimal'``, ``'rinf'`` and ``'rsup'``
    
        **Output directory** is the location where the downloaded files will be saved.
        
        **Output filename** is the name of the downloaded file. If not specified, a default name will be used.

        .. note::
        
            When specifying ``output_filename``, be mindful of the appropriate file extension:
            
            When downloading a **single file** : match the extension to the file type (e.g., ``output_filename="lightcurve.fits"``) or leave ``output_filename`` as ``None`` to use the default name
            When downloading **multiple files** : use a ``.tar`` or ``.tar.gz`` extension (e.g., ``output_filename="my_data.tar.gz"``) or leave ``output_filename`` as ``None`` to use the default name
            

        :param filters: Filters to apply to the query
        :type filters: dict
        :param file_type: The type of files to download
        :type file_type: str
        :param aperture: The aperture (``'default'``, ``'optimal'``, ``'rinf'``, ``'rsup'``)
        :type aperture: Optional[str]
        :param compressed: Specify whether to compress the downloaded files. (``True`` for ``.tar.gz``, ``False`` for ``.tar``)
        :type compressed: Optional[bool]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The filename for the download
        :type output_filename: Optional[str]
        :return: None


        .. dropdown:: Downloading all products for a given visit
            :color: success
            :icon: code-square

            .. code-block:: python
            
                from dace_query.cheops import Cheops
                filters_to_use = {'file_key': {'contains': ['CH_PR300001_TG000301_V0000']}}
                Cheops.download(filters_to_use)
        
        .. dropdown:: Downloading a specific product type (eg. lightcurves) for a given visit
            :color: success
            :icon: code-square

            .. code-block:: python
            
                from dace_query.cheops import Cheops
                filters_to_use = {'file_key': {'contains': ['CH_PR300001_TG000301_V0000']}}
                Cheops.download(filters=filters, file_type='lightcurves')
                
        """
        if file_type not in self.__ACCEPTED_FILE_TYPES:
            raise ValueError('file_type must be one of these values : ' + ','.join(self.__ACCEPTED_FILE_TYPES))
        if filters is None:
            filters = {}

        if aperture is not None and file_type not in ['lightcurves', 'mp4']:
            raise ValueError('aperture can only be used with file_type = lightcurves or mp4')

        download_id = self.dace.request_post(
            api_name=self.__CHEOPS_API,
            endpoint='download',
            data=json.dumps({
                'fileType': file_type,
                'filters': filters,
                'aperture': aperture
                })
        )
        if not download_id:
            return None

        self.dace.persist_file_on_disk(
            api_name=self.__CHEOPS_API,
            obs_type='photometry',
            params={'compressed': compressed},
            download_id=download_id['key'],
            output_directory=output_directory,
            output_filename=output_filename
        )

    def download_files(self,
                       files: list,
                       file_type: Optional[str] = 'all',
                       output_directory: Optional[str] = None,
                       output_filename: Optional[str] = None):
        """
        

        .. deprecated:: 2.0.0
        
            This method is no longer supported and will be removed in a future version.
            Use :meth:`download` instead.
        
        Download reduction products specified in argument for the list of raw specified and save it locally.

        File type available are ['lightcurves', 'images', 'reports', 'full', 'sub', 'all', 'files'].

        **Note:** When using ``file_type='files'``, it is necessary to indicate the **exact filename** of each data product that will be downloaded (See :doc:`usage_examples`).

        :param files: The raw files
        :type files: list[str]
        :param file_type: The type of files to download
        :type file_type: Optional[str]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename: The file for the download
        :type output_filename: Optional[str]
        :return: None


        .. dropdown:: (Outdated) Downloading reduction products using file paths
            :color: warning
            :icon: code-square
            
            .. code-block:: python

                from dace_query.cheops import Cheops
                Cheops.download_files(files=['cheops/outtray/PR30/PR300024_TG000101_V0101/CH_PR300024_TG000101_TU2020-03-09T14-50-41_SCI_RAW_SubArray_V0101.fits'],file_type='lightcurves',output_directory='/tmp' ,output_filename='cheops.tar.gz')
                Cheops.download_files(files=['cheops/outtray/PR30/PR300024_TG000101_V0101/CH_PR300024_TG000101_TU2020-03-09T14-50-41_SCI_RAW_HkCe-SubArray_V0101.fits', 'cheops/outtray/PR30/PR300024_TG000101_V0101/CH_PR300024_TG000101_TU2020-03-09T14-49-35_SCI_RAW_HkCe-FullArray_V0101.fits'], file_type='files', output_directory='/tmp', output_filename='specific_files.tar.gz')
        """
        raise NotImplementedError(
            "CheopsClass.download_files() is no longer supported as of version 2.0.0."
            "Please use CheopsClass.download() instead. "
            "See documentation at https://dace-query.readthedocs.io/en/latest/dace_query.cheops.html"
        )

        if files is None:
            raise NoDataException
        files = list(map(lambda file: f'{file}.fits' if not file.endswith('.fits') else file, files))
        download_response = self.dace.request_post(
            api_name=self.__CHEOPS_API,
            endpoint='download',
            data=json.dumps(
                {'fileType': file_type, 'files': files}
            )
        )
        if not download_response:
            return None
        self.dace.persist_file_on_disk(
            api_name=self.__CHEOPS_API,
            obs_type='photometry',
            download_id=download_response['key'],
            output_directory=output_directory,
            output_filename=output_filename
        )

    def download_diagnostic_movie(self,
                                  file_key: str,
                                  aperture: Optional[str] = 'default',
                                  output_directory: Optional[str] = None,
                                  output_filename: Optional[str] = None) -> None:
        """
        
        .. deprecated:: 2.0.0
        
            This method is deprecated and will be removed in a future version.
            Use :meth:`download` with ``file_type='mp4'`` instead.

        Download diagnostic movie for a Cheops file_key.

        Aperture types available are : ``'default'``, ``'optimal'``, ``'rinf'`` and ``'rsup'``

        :param file_key: The cheops visit file key
        :type file_key: str
        :param aperture: Apertures types
        :type aperture: Optional[str]
        :param output_directory: The directory where files will be saved
        :type output_directory: Optional[str]
        :param output_filename:  The filename for the download
        :type output_filename: Optional[str]
        :return: None

        .. dropdown:: (Outdated) Downloading diagnostic movies using file keys
            :color: warning
            :icon: code-square

            .. code-block:: python

                from dace_query.cheops import Cheops
                Cheops.download_diagnostic_movie(file_key='CH_PR100018_TG027204_V0200', output_directory='/tmp', output_filename='cheops_movie.mp4')

        """
        warnings.warn(
            "CheopsClass.download_diagnostic_movie() is deprecated and will be removed in future versions of dace-query"
            "Use CheopsClass.download() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        filters: dict = {'file_key':{'equal': [file_key]}}

        self.download(
                 file_type='mp4',
                 aperture=aperture,
                 filters=filters,
                 output_directory=output_directory,
                 output_filename=output_filename)
        


    def list_data_product(self,
                          visit_filepath: str,
                          output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        .. deprecated:: 2.0.0
            This method is no longer supported and will be removed in a future version.
            Use :meth:`browse_products` with ``filters`` instead:
            
            .. code-block:: python
            
                filters: dict = {'target_name': {'contains': 'TOI178'}}
                browse_products(filters=filters)

        List the filenames of all available data products for the specified visit filepath.

        :param visit_filepath: The cheops visit filepath
        :type visit_filepath: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: (Outdated) Listing data products using visit file paths
            :color: warning
            :icon: code-square

            .. code-block:: python

                from dace_query.cheops import Cheops
                values = Cheops.list_data_product(visit_filepath='cheops/outtray/PR10/PR100018_TG027204_V0200/CH_PR100018_TG027204_TU2020-12-04T04-42-41_SCI_RAW_SubArray_V0200.fits')
        """
        
        data = json.dumps({'file_rootpath': [visit_filepath]})
        
        products = self.dace.request_post(api_name=self.__CHEOPS_API, endpoint='download/browse',data=data)
        return self.dace.transform_to_format(products, output_format=output_format)

    def browse_products(self,
                filters: dict,
                file_type: str = 'all',
                aperture: Optional[str] = None,
                output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        List the filenames of all available data products for visits matching the specified filters.
        
        This method mirrors the signature of :meth:`download`, making it ideal for previewing available data products 
        before performing any actual downloads. Use it to examine what files would be retrieved based on your 
        filters, file_type, and aperture settings.
        
        You **must** specify filtering criteria (such as target name, file key, or other parameters) to limit the scope of the operation. 
        This requirement helps avoid unintentionally requesting large amounts of data from the CHEOPS database.
        **Filters** can be applied to the query via named arguments (see :doc:`query_options`).
        
        .. dropdown:: Setting filters
            :color: primary
            :icon: code-square
        
            .. code-block:: python
            
                # Filtering using file_key
                file_key = 'CH_PR100018_TG027204_V0200'
                filters: dict = {'file_key':{'equal': [file_key]}}
            
            .. code-block:: python
            
                # Filtering using target_name
                target_name = 'TOI178'
                filters: dict = {'target_name':{'equal': [target_name]}}

        **File types** can be specified in two ways:

        .. dropdown:: General categories
            :color: info
            :icon: list-unordered
    
            * ``lightcurves``
            * ``images``
            * ``reports``
            * ``full``
            * ``sub``
            * ``all``


        .. dropdown:: Specific CHEOPS product identifiers
            :color: info
            :icon: list-unordered

            * ``EXT_PRE_StarCatalogue``
            * ``MCO_REP_BadPixelMapFullArray``
            * ``MCO_REP_BadPixelMapSubArray``
            * ``MCO_REP_DarkFrameFullArray``
            * ``MCO_REP_DarkFrameSubArray``
            * ``PIP_COR_PixelFlagMapSubArray``
            * ``PIP_REP_DarkColumns``
            * ``SCI_CAL_SubArray``
            * ``SCI_COR_Lightcurve``
            * ``SCI_COR_SubArray``
            * ``SCI_RAW_FullArray``
            * ``SCI_RAW_Imagette``
            * ``SCI_RAW_SubArray``
            * ``SCI_RAW_Attitude``
            * ``SCI_RAW_Centroid``
            * ``SCI_RAW_EventReport``
            * ``SCI_RAW_HkAsy30759``
            * ``SCI_RAW_HkAsy30767``
            * ``SCI_RAW_HkCe``
            * ``SCI_RAW_HkCentroid``
            * ``SCI_RAW_HkDefault``
            * ``SCI_RAW_HkExtended``
            * ``SCI_RAW_HkIaswPar``
            * ``SCI_RAW_HkIfsw``
            * ``SCI_RAW_HkOperationParameter``
            * ``log``
            * ``mp4``
            * ``pdf``
        
        **Aperture** can be used to further filter products.
        It is useful in the case where we need to download a single specific ``lightcurves`` or ``mp4`` data product.
        Setting the aperture on other file types is not supported and will raise an error.
        
        Aperture types available are : ``'default'``, ``'optimal'``, ``'rinf'`` and ``'rsup'``

        :param filters: Filters to apply to the query
        :type filters: dict
        :param file_type: The type of files to download
        :type file_type: str
        :param aperture: The aperture (``'default'``, ``'optimal'``, ``'rinf'``, ``'rsup'``)
        :type aperture: Optional[str]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict


        .. dropdown:: Listing all available products for a given target name
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.cheops import Cheops
                values = Cheops.browse_products(filters={'target_name':{'equal': [target_name]}})
                

        .. dropdown:: Listing all available lightcurves for a given target name
            :color: success
            :icon: code-square
            
            .. code-block:: python

                from dace_query.cheops import Cheops
                values = Cheops.browse_products(filters={'target_name':{'equal': [target_name]}}, file_type='lightcurves')
                
        """
        
        if file_type not in self.__ACCEPTED_FILE_TYPES:
            raise ValueError('file_type must be one of these values : ' + ','.join(self.__ACCEPTED_FILE_TYPES))
        
        if filters is None:
            filters = {}

        if aperture is not None and file_type not in ['lightcurves', 'mp4']:
            raise ValueError('aperture can only be used with file_type = lightcurves or mp4')
            
            
        products = self.dace.request_post(
            api_name=self.__CHEOPS_API,
            endpoint='download/browse',
            data=json.dumps({
                'fileType': file_type,
                'filters': filters,
                'aperture': aperture
                })
        )
        return self.dace.transform_to_format(products, output_format=output_format)

Cheops: CheopsClass = CheopsClass()
"""
This is a singleton instance of the :class:`CheopsClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.cheops import Cheops
"""