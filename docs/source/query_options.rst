Filtering and sorting
#####################

Filters
*******

Dace proposes for certain queries the use of filters through the ``filters`` argument.

The filters work in the same way as those offered on the `DACE <https://dace.unige.ch>`_ online site.
They consist of a dictionary type object (*key-value*), where the *key* is the parameter that we want to filter and the
*value* will be the desired filtering operation.

**Here is an example :**

.. code-block:: python

    # A python dictionary defining a filter
    # In key the parameter to filter : obj_id_catname
    # In value the filtering operation: contains

    # This will filter all data containing "HD" in the obj_id_catname parameter
    filters: dict = {
        'obj_id_catname': {
            'contains': ['HD']
        }
    }


Filterable parameters
=====================

There are different **filterable parameters** and those are retrievable for each module using the ``query_database`` function.

**Here is an example to get the filterable parameters of the exoplanet module :**

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    result: dict = Exoplanet.query_database(limit=10, output_format='dict')

    # The parameters for the exoplanet module
    exoplanet_parameter_names = list(result.keys()))


Available filters
=================

contains - not contains
-----------------------

This filter filters the chosen parameter if it contains or not the value sought.

These two filters can be applied to *string* type parameters.

**Example :** *It returns planets that do not contain "HD" in their name.*

.. code-block:: python

    from dace_query.exoplanet import Exoplanet

    # not contains
    filters: dict = {
        'obj_id_catname': {
            'notContains': ['HD']
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


**Example :** *It returns planets that contain "HD" in their name.*

.. code-block:: python

    # contains
    filters: dict = {
        'obj_id_catname': {
            'contains': ['HD']
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)



equal - not equal
-----------------

This filter filters the chosen parameter if it is equal or not to the value sought.

These two filters can be applied to *string*, *float* and *int* type parameters.

**Example :** *It returns planets with names not equal to "Kepler-444 A e" and "Gliese 433 c".*

.. code-block:: python

    from dace_query.exoplanet import Exoplanet

    # not equal
    filters: dict = {
        'obj_id_catname': {
            'notEqual': ['Kepler-444 A e', 'Gliese 433 c']
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


**Example :** *It returns planets with names equal to "Kepler-444 A e" and "Gliese 433 c".*

.. code-block::python

    # equal
    filters: dict = {
        'obj_id_catname': {
            'equal': ['Kepler-444 A e', 'Gliese 433 c']
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


empty
-----

This filter filters the chosen parameter depending on whether its value is empty or not.

This filter can be applied to *string* and *boolean* type parameters.

**Example :** *It returns planets where publication link is available.*

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    filters: dict = {
        'pub_ads_link': {
            'empty': False
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


min - max
---------

This filter filters the chosen parameter if its value is between the specified minimum and maximum.

This filter can be applied to *float* and *int* type parameters.

**Example :** *It returns planets with mass between 0.01 and 0.04 Jupiter mass.*

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    filters: dict = {
        'obj_phys_mass_mjup': {
            'min': 0.01,
            'max': 0.04
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


is
--

This filter filters the chosen parameter depending on whether its value is *True* or *False*.

This filter can be applied to *boolean* type parameters.

**Example:** *It returns spectroscopic observations where the spectrum is available.*

.. code-block:: python

    from dace_query.spectroscopy import Spectroscopy
    filters: dict = {
        'db_spectrum_available': {
            'is': True
        }
    }
    values = Spectroscopy.query_database(filters=filters, limit=10)


Advanced usage example
======================

The parameters to be filtered and the filters themselves can be combined.

**Here is an example :**

It returns planets :

- with name containing "TOI" and "HD" but not equal to "TOI-755 b'
- ( and ) with orbital period between "2.5" and "3" days
- ( and ) detected by the "RV" (Radial Velocity) method

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    filters: dict = {
        'obj_id_catname': {
            'contains':
                ['TOI', 'HD'],
            'notEqual': ['TOI-755 b']
        },
        'obj_orb_period_day': {
            'min': 2.5,
            'max': 3
        },
        'pub_info_detectiontype': {
            'equal': ['RV']
        }
    }
    values = Exoplanet.query_database(filters=filters, limit=10)


Sort order
**********

Dace proposes for certain queries to sort parameters through the ``sort`` argument.

The sort works in the same way as the one offered on the `DACE <https://dace.unige.ch>`_ online site.

It consists of a dictionary type object (*key-value*), where the *key* is the parameter that we want to sort and the
*value* will be the desired sort order.

**Example :** *It returns recently discovered planets, sorted descending by the discovered year.*

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    sort: dict = {'pub_info_discovered_year': 'desc'}

    values = Exoplanet.query_database(sort=sort, limit=10)


**Example :** *It returns planets with the smallest orbital period, sorted ascending by the orbital period.*

.. code-block:: python

    from dace.exoplanet import Exoplanet
    sort: dict = {'obj_orb_period_day': 'asc'}
    values = Exoplanet.query_database(sort=sort, limit=10)

Advanced usage example
======================

The sort filter can be applied on multiple parameters at the same time.

**Here is an example :**

It returns planets:

- sorted ascending by the radius
- ( and then ) sorted descending by name

.. code-block:: python

    from dace_query.exoplanet import Exoplanet
    sort: dict = {
        'obj_phys_radius_rjup': 'asc',
        'obj_id_catname': 'desc'
    }
    values = Exoplanet.query_database(sort=sort, limit=10)


