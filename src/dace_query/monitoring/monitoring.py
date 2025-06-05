from __future__ import annotations

import logging
from typing import Optional, Union

from astropy.table import Table
from numpy import ndarray
from pandas import DataFrame

from dace_query import Dace, DaceClass

MONITORING_DEFAULT_LIMIT = 10000


class MonitoringClass:
    """
    The monitoring class.
    Use to retrieve data from the monitoring module.

    .. tip::
    
        A monitoring instance is already provided, to use it:
        
        .. code-block:: python
        
            from dace_query.monitoring import Monitoring
    """


    def __init__(self, dace_instance: DaceClass = None):
        """
        Create a configurable monitoring object which uses a specified dace instance.

        :param dace_instance: A dace object
        :type dace_instance: Optional[DaceClass]

        .. code-block:: python

            from dace_query.monitoring import MonitoringClass
            monitoring_instance = MonitoringClass()
        """
        self.__MONITORING_API = 'monitoring-webapp'

        if dace_instance is None:
            self.dace = Dace
        elif isinstance(dace_instance, DaceClass):
            self.dace = dace_instance
        else:
            raise Exception("Dace instance is not valid")

        # Logger configuration
        unique_logger_id = self.dace.generate_short_sha1()
        logger = logging.getLogger(f"monitoring-{unique_logger_id}")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.log = logger

    def query_transfer_by_night(self,
                                instrument: str, pipeline: str, night: str,
                                output_format: Optional[str] = None
                                ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the monitoring database to retrieve data in the chosen format for the specified instrument, night and
        pipeline.

        All available formats are defined in this section (see :doc:`output_format`).

        Available pipeline names are:
        
        - ``TRANSFER``: From remote archive to Geneva archive (Transfer)
        - ``GENEVA``: From reduction in Geneva to DACE import (Reduction and import)
        - ``FULL``: From remote archive to DACE import (Transfer, reduction and import)

        The supported combinations are indicated below :

        .. list-table:: Possible instrument/pipeline combinations
            :header-rows: 1
            
            * - Instrument name
              - Pipeline name
              
            * - ``'HARPS'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'ESPRESSO'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'CORALIE14'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'ECAM'``
              - ``'TRANSFER'``
              
            * - ``'HARPN'``
              - ``'TRANSFER'``

        :param instrument: The instrument name
        :type instrument: str
        :param pipeline: The pipeline name
        :type pipeline: str
        :param night: The date of the night
        :type night: str
        :param output_format: Type of data returns
        :type output_format: Optional[strs]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the monitoring data for a specific night, instrument and pipeline
            :color: success
            :icon: code-square

            .. code-block:: python

              from dace_query.monitoring import Monitoring
              values = Monitoring.query_transfer_by_night(instrument='HARPS', pipeline='FULL', night='2022-11-08')
        """

        complete_name = f"{instrument}_{pipeline}".upper()

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__MONITORING_API,
                endpoint=f'monitoring/{complete_name}/date/{night}'),
            output_format=output_format
        )

    def query_transfer_by_period(self, instrument: str, pipeline: str, period: tuple[str, str],
                                 output_format: Optional[str] = None
                                 ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the monitoring database ot retrieve data in the chosen format for the specified instrument, period and
        pipeline.

        All available formats are defined in this section (see :doc:`output_format`).


        Available pipeline names are:
        
        - ``TRANSFER``: From remote archive to Geneva archive (Transfer)
        - ``GENEVA``: From reduction in Geneva to DACE import (Reduction and import)
        - ``FULL``: From remote archive to DACE import (Transfer, reduction and import)

        The supported combinations are indicated below :

        .. list-table:: Possible instrument/pipeline combinations
            :header-rows: 1
            
            * - Instrument name
              - Pipeline name
              
            * - ``'HARPS'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'ESPRESSO'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'CORALIE14'``
              - ``'TRANSFER'`` or ``'GENEVA'`` or ``'FULL'``
              
            * - ``'ECAM'``
              - ``'TRANSFER'``
              
            * - ``'HARPN'``
              - ``'GENEVA'``

        :param instrument: The instrument name
        :type instrument: str
        :param pipeline: The pipeline name
        :type pipeline: str
        :param period: The periods
        :type period: tuple[str, str]
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the monitoring data for a specific period, instrument and pipeline
            :color: success
            :icon: code-square

            .. code-block:: python

              from dace_query.monitoring import Monitoring
              values = Monitoring.query_transfer_by_period(instrument='HARPS', pipeline='FULL', period=('2022-11-07', '2022-11-09'))
        """

        complete_name = f"{instrument}_{pipeline}".upper()

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__MONITORING_API,
                endpoint=f'monitoring/{complete_name}/period/{period[0]}/{period[1]}'),
            output_format=output_format)

    def query_transfer_by_program(self, instrument: str, pipeline: str, program: str,
                                  output_format: Optional[str] = None
                                  ) -> Union[dict[str, ndarray], DataFrame, Table, dict]:
        """
        Query the monitoring database to retrieve data in the chosen format for the specified instrument, pipeline and
        program.

        All available formats are defined in this section (see :doc:`output_format`).


        Available pipeline names are:
        
        - ``TRANSFER``: From remote archive to Geneva archive (Transfer)
        - ``GENEVA``: From reduction in Geneva to DACE import (Reduction and import)
        - ``FULL``: From remote archive to DACE import (Transfer, reduction and import)


        The supported combinations are indicated below :
        
        .. list-table:: Possible instrument/pipeline combinations
            :header-rows: 1
            
            * - Instrument
              - Pipeline
              
            * - ``'HARPS'``
              - ``'TRANSFER'`` or ``'FULL'``
              
            * - ``'ESPRESSO'``
              - ``'TRANSFER'`` or ``'FULL'``




        :param instrument: The instrument name
        :type instrument: str
        :param pipeline: The pipeline name
        :type pipeline: str
        :param program: The program name
        :type program: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the monitoring data for a specific program, instrument and pipeline
            :color: success
            :icon: code-square

            .. code-block:: python

              from dace_query.monitoring import Monitoring
              values = Monitoring.query_transfer_by_program(instrument='ESPRESSO', pipeline='TRANSFER', program='110.245W.001')

        """

        complete_name = f"{instrument}_{pipeline}".upper()

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__MONITORING_API,
                endpoint=f'monitoring/{complete_name}/program/{program}'),
            output_format=output_format)

    def query_transfer_by_target(self,
                                 instrument: str, pipeline: str, target: str,
                                 output_format: Optional[str] = None
                                 ):
        """
        Query the monitoring database to retrieve data in the chosen format for the specified instrument, pipeline and
        target.

        All available formats are defined in this section (see :doc:`output_format`).


        Available pipeline names are:
        
        - ``'TRANSFER'``: From remote archive to Geneva archive (Transfer)
        - ``'GENEVA'``: From reduction in Geneva to DACE import (Reduction and import)
        - ``'FULL'``: From remote archive to DACE import (Transfer, reduction and import)

        The supported combinations are indicated below :
        
        .. list-table:: Possible instrument/pipeline combinations
            :header-rows: 1
            
            * - Instrument
              - Pipeline
              
            * - ``'HARPS'``
              - ``'TRANSFER'`` or ``'FULL'``
              
            * - ``'ESPRESSO'``
              - ``'TRANSFER'`` or ``'FULL'``

        :param instrument: The instrument name
        :type instrument: str
        :param pipeline: The pipeline name
        :type pipeline: str
        :param target: The target name
        :type target: str
        :param output_format: Type of data returns
        :type output_format: Optional[str]
        :return: The desired data in the chosen output format
        :rtype: dict[str, ndarray] or DataFrame or Table or dict

        .. dropdown:: Getting the monitoring data for a specific target, instrument and pipeline
            :color: success
            :icon: code-square

            .. code-block:: python

              from dace_query.monitoring import Monitoring
              values = Monitoring.query_transfer_by_target(instrument='ESPRESSO', pipeline='TRANSFER', target='L 513-23')
        """

        complete_name = f"{instrument}_{pipeline}".upper()

        return self.dace.transform_to_format(
            self.dace.request_get(
                api_name=self.__MONITORING_API,
                endpoint=f'monitoring/{complete_name}/target/{target}'),
            output_format=output_format
        )


Monitoring: MonitoringClass = MonitoringClass()
"""
This is a singleton instance of the :class:`MonitoringClass` class.

To use it, simply import it :

.. code-block:: python

    from dace_query.monitoring import Monitoring
"""