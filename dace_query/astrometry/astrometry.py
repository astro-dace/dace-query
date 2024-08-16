from __future__ import annotations

import json
import logging
import re
from typing import Optional, Union

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

ASTROMETRY_DEFAULT_LIMIT = 10000


class AstrometryClass:
    """
    The astrometry class.
    Use to retrieve data from the astrometry module.

    **An astrometry instance is already provided, to use it :**

    >>> from dace_query.astrometry import Astrometry

    """

    def __init__(self, dace_instance: Optional[DaceClass] = None):
        """
        Create a configurable astrometry object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        >>> from dace_query.astrometry import AstrometryClass
        >>> astrometry_instance = AstrometryClass()

        """

        # Logging configuration
        self.__OBSERVATION_API = "obs-webapp"
        self.__ASTROMETRY_API = "astrom-webapp"

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"astrometry-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def _check_id(self, id: str) -> str:
        """
        Check if the given id is valid.

        :param id: The id to check
        :type id: str
        :return: The id if it is valid
        :rtype: str
        """
        # Validate the input type
        if not isinstance(id, str):
            raise TypeError("The identifier must be a string.")

        # Normalize the input
        id = id.strip().upper()
        id = re.sub(r"\s+", " ", id)  # Replace multiple spaces with a single space

        # Identify the catalog and validate format
        catalog = None
        id_number = None

        if id.startswith("HIP"):
            catalog = "HIP"
            id_number = id[3:].strip()  # Extract number after "HIP"
            if not id_number.isdigit() or len(id_number) > 6:
                raise ValueError("Invalid HIP identifier format.")
        elif id.startswith("GAIA DR3"):
            catalog = "GAIA DR3"
            id_number = id[8:].strip()  # Extract number after "GAIA DR3"
            if not id_number.isdigit() or len(id_number) <= 6:
                raise ValueError("Invalid Gaia DR3 identifier format.")
        else:
            # Assume it's a number only, determine catalog based on length
            id_number = id.strip()
            if id_number.isdigit():
                if len(id_number) <= 6:
                    catalog = "HIP"
                else:
                    catalog = "GAIA DR3"
            else:
                raise ValueError(
                    "Identifier must be a valid number or a recognized catalog prefix (HIP, Gaia DR3)."
                )

        return catalog, id_number

    def query_hipparcos_database(self, id: str, output_format: str = None):
        """
        Query hipparcos database to retrieve data from the main hipparcos catalog with the
        basic information about a targets and its solution. Can be queried either with an Hipparcos
        identifier, or with a Gaia DR3 identifier. Returns an error if both or none are given.

        :param id: Identifier of the target, either a HIP id or a Gaia DR3 id
        :type id: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict
        :param output_format: The format you want for result data : numpy, pandas, astropy_table (default (None) dict)
        :type output_format: str
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. code-block:: python

            from dace.astrometry import Astrometry

            # Query the Hipparcos database with a Hipparcos identifier
            Astrometry.query_hipparcos_database('HIP 1000', output_format='pandas')

            # Query the Hipparcos database with a Gaia DR3 identifier
            Astrometry.query_hipparcos_database('Gaia DR3 2361372542600289664', output_format='pandas')
        """
        # Validate the input type
        catalog, id_number = self._check_id(id)

        # Query the backend
        if catalog == "HIP":
            backend_endpoint = f"hipparcos/model/hip/{id_number}"
        elif catalog == "GAIA DR3":
            backend_endpoint = f"hipparcos/model/gaia/{id_number}"

        return self.dace.transform_to_format(
            self.dace.request_get(
                self.__ASTROMETRY_API,
                backend_endpoint,
            ),
            output_format=output_format,
        )

    def get_hipparcos_timeseries(self, id: str, output_format: str = None):
        """
        Get the timeseries from the Hipparcos Intermediate Astrometric Data (IAD). Can be queried either with an Hipparcos
        identifier, or with a Gaia DR3 identifier. Returns an error if both or none are given.

        All available formats are defined in this section (see :doc:`output_format`).

        :param hip_id: Hipparcos identifier
        :type hip_id: int
        :param gaia_id: Gaia DR3 identifier
        :type gaia_id: int
        :param output_format: (optional) the format you want for result data : numpy, pandas, astropy_table (default (None) dict)
        :type output_format: str
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. code-block:: python

            from dace.astrometry import Astrometry

            Astrometry.get_hipparcos_timeseries(hip_id=1000, output_format='pandas')

        """

        # Validate the input type
        catalog, id_number = self._check_id(id)

        # Query the backend
        if catalog == "HIP":
            backend_endpoint = f"hipparcos/iad/hip/{id_number}"
        elif catalog == "GAIA DR3":
            backend_endpoint = f"hipparcos/iad/gaia/{id_number}"

        return self.dace.transform_to_format(
            self.dace.request_get(
                self.__ASTROMETRY_API,
                backend_endpoint,
            ),
            output_format=output_format,
        )

    def query_database(
        self,
        limit: Optional[int] = ASTROMETRY_DEFAULT_LIMIT,
        filters: Optional[dict] = None,
        sort: Optional[dict] = None,
        output_format: Optional[str] = None,
    ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the astrometry database to retrieve data in the chosen format.

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

        >>> from dace_query.astrometry import Astrometry
        >>> values = Astrometry.query_database()
        """

        if filters is None:
            filters = {}
        if sort is None:
            sort = {}

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__OBSERVATION_API,
                endpoint="observation/search/astrometry",
                params={
                    "limit": str(limit),
                    "filters": json.dumps(filters),
                    "sort": json.dumps(sort),
                },
            ),
            output_format=output_format,
        )

    def get_gaia_timeseries(
        self, target: str, output_format: Optional[str] = None
    ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Get timeseries from Gaia astrometry for the specified target.

        All available formats are defined in this section (see :doc:`output_format`).

        :param target: The target name to retrieve astrometry data from
        :type target: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        >>> from dace_query.astrometry import Astrometry
        >>> target_to_search = 'your-target'
        >>> values = Astrometry.get_gaia_timeseries(target=target_to_search)

        """

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__OBSERVATION_API,
                endpoint=f"observation/astrometry/{target}",
            ),
            output_format=output_format,
        )


Astrometry: AstrometryClass = AstrometryClass()
"""
Astrometry instance
"""
