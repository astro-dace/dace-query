from __future__ import annotations

import json
import logging
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

    def query_hipparcos_database(
        self,
        hip_id: int = None,
        gaia_id: int = None,
        output_format: str = None,
    ):
        """
        Query hipparcos database to retrieve data from the main hipparcos catalog with the
        basic information about a targets and its solution. Can be queried either with an Hipparcos
        identifier, or with a Gaia DR3 identifier. Returns an error if both or none are given.

        :param hip_id: Hipparcos identifier
        :param gaia_id: Gaia DR3 identifier
        # :param limit: the max number of rows to retrieve
        # :param filters: A dict to apply filters on columns (see example below)
        # :param sort: A dict describing the sorting results (see example below)
        :param output_format: (optional) the format you want for result data : numpy, pandas, astropy_table (default (None) dict)
        :return: A dict containing lists of values

        .. code-block:: python

            # ToDo: Complete documentation
        """
        if not hip_id and not gaia_id:
            raise ValueError("Please provide either a HIP id or a Gaia DR3 id.")
        if hip_id and gaia_id:
            raise ValueError(
                "Both a HIP id and a Gaia id were given. Please only provide one."
            )

        if hip_id:
            return self.dace.transform_to_format(
                self.dace.request_get(
                    self.__ASTROMETRY_API,
                    f"hipparcos/model/hip/{hip_id}",
                ),
                output_format=output_format,
            )
        elif gaia_id:
            return self.dace.transform_to_format(
                self.dace.request_get(
                    self.__ASTROMETRY_API,
                    f"hipparcos/model/gaia/{gaia_id}",
                ),
                output_format=output_format,
            )

    def get_hipparcos_timeseries(
        self, hip_id: int = None, gaia_id: int = None, output_format: str = None
    ):
        """
        Get the timeseries from the Hipparcos Intermediate Astrometric Data.

        :param hip_id: Hipparcos identifier
        :param gaia_id: Gaia DR3 identifier
        :param output_format: (optional) the format you want for result data : numpy, pandas, astropy_table (default (None) dict)
        :return: a dict containing astrometry timeseries vectors

        .. code-block:: python

            from dace.astrometry import Astrometry

            # TODO: Complete documentation

        """

        if not hip_id and not gaia_id:
            raise ValueError("Please provide either a HIP id or a Gaia DR3 id.")
        if hip_id and gaia_id:
            raise ValueError(
                "Both a HIP id and a Gaia id were given. Please only provide one."
            )

        if hip_id:
            return self.dace.transform_to_format(
                self.dace.request_get(
                    self.__ASTROMETRY_API, f"hipparcos/iad/hip/{hip_id}"
                ),
                output_format=output_format,
            )
        elif gaia_id:
            return self.dace.transform_to_format(
                self.dace.request_get(
                    self.__ASTROMETRY_API, f"hipparcos/iad/gaia/{gaia_id}"
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
