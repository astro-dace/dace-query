from __future__ import annotations

import json
import logging
from typing import Optional, Union

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

CATALOG_DEFAULT_LIMIT = 10000


class CatalogClass:
    """
    The catalog class.
    Use to retrieve data from the catalog module.

    .. tip::
        
        A catalog instance is already provided, to use it:

        .. code-block:: python

            from dace_query.catalog import Catalog

    """

    def __init__(self, dace_instance: DaceClass = None):
        """
        Create a configurable catalog object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]


        .. code-block:: python
        
            from dace_query.catalog import CatalogClass
            catalog_instance = CatalogClass()

        """

        self.__OBSERVATION_API = 'obs-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"catalog-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_database(self, catalog: str,
                       limit: Optional[int] = CATALOG_DEFAULT_LIMIT,
                       filters: Optional[dict] = None,
                       sort: Optional[dict] = None,
                       output_format: Optional[str] = None) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the catalog database to retrieve data in the chosen format.

        Filters and sorting order can be applied to the query via named arguments (see :doc:`query_options`).

        All available formats are defined in this section (see :doc:`output_format`).

        .. dropdown:: Available catalogs
            :color: info
            :icon: list-unordered
            :open:
        
            * ``'k2-epic'``
            * ``'coralie-714'``
            * ``'coralie-703'``
            * ``'gaiataskforce'``
            * ``'k2-confirmed-planets'``
            * ``'cascades'``

        .. seealso::
        
            The CHEOPS Catalogs, TOI catalog and TESS Input Catalog are available in their respective modules.
            
            * :class:`~dace_query.tess.tess` - :meth:`~dace_query.tess.tess.TessClass.query_toi_catalog`
            * :class:`~dace_query.tess.tess` -  :meth:`~dace_query.tess.tess.TessClass.query_tic_catalog`
            * :class:`~dace_query.cheops.cheops` -  :meth:`~dace_query.cheops.cheops.CheopsClass.query_catalog`

        :param catalog: The catalog name to retrieve
        :type catalog: str
        :param limit: Maximum number of rows to return
        :type limit: Optional[int]
        :param filters: Filters to apply to the query
        :type filters: Optional[dict]
        :param sort: Sort order to apply to the query
        :type sort: Optional[dict]
        :param output_format: Type of data returns
        :type output_format: str
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the K2 EPIC catalog
            :color: success
            :icon: code-square

            .. code-block:: python
            
                from dace_query.catalog import Catalog
                catalog_to_search = 'k2-epic'
                values = Catalog.query_database(catalog=catalog_to_search)

        """

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        if catalog == 'toi' or catalog == 'tess':
            raise NotImplementedError(
                "The TOI catalog and TESS Input Catalog are available in the Tess module."
                "from dace_query.tess import Tess"
                "values = Tess.query_toi_catalog() # TOI catalog"
                "values = Tess.query_tic_catalog() # TESS Input Catalog"
            )
        if catalog == 'cheops':
            raise NotImplementedError(
                "The CHEOPS catalog is available in the Cheops module."
            )

        # Associative array to convert the catalog name to the API name
        catalog_ids = {
            # 'tess': 1, # Moved to the tess module
            'k2-epic': 2,
            # 'toi': 3, # Moved to the tess module
            'coralie-714': 4,
            '714': 4,
            'coralie-703': 5,
            '703': 5,
            'gaiataskforce': 6,
            #'cheops-planets': 7,
            #'cheops-stars': 8,
            'k2-confirmed-planets': 9,
            'cascades': 10
        }

        # Get the catalog id to query the api
        catalog_id = catalog_ids.get(catalog, None)
        
        if catalog_id is None:
            raise ValueError(f"Catalog {catalog} not found. Available catalogs are: {list(catalog_ids.keys())}")

        return self.dace.transform_to_format(
            self.dace.request_get(
            api_name=self.__OBSERVATION_API,
            endpoint=f'catalog/{catalog_id}',
            params={
                'limit': str(limit),
                'filters': json.dumps(filters),
                'sort': json.dumps(sort)
            }
            ), output_format=output_format)


Catalog: CatalogClass = CatalogClass()
"""

This is a singleton instance of the :class:`CatalogClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.catalog import Catalog
"""