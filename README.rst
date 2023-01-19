dace-query
##########

Description
***********
The dace-query package lets easily query DACE and access public and private data using a simple utility tool.

Installation
************

The dace-query package is available on PyPi and can be installed using `pip <https://pypi.org/project/pip/>`_ or `conda <https://www.anaconda.com>`_:


.. code-block:: bash

    # Install using pip
    pip install dace-query

    # Update using pip
    pip install dace-query --upgrade

.. code-block:: bash

    # Install using conda
    # First, create a conda environment
    conda create -n <env_name> python=3.9 # python version equal or upper than 3.9
    # Second, activate the environment
    conda activate <env_name>
    # Finally, install using anaconda pip
    pip install dace-query

Make sure the package is installed correctly :

.. code-block:: python

    # Import dace
    import dace_query

    # List content of the dace package
    help(dace)

Authentication
**************

In order to access the private data of DACE, an authentication system has been implemented.
This one works very simply, it just requires three things detailed in the following subsections:


- A DACE account
- An API key
- A local .dacerc file


.. _create-account:

1. Create an account
====================
Register on the `DACE web portal <https://dace.unige.ch/createAccount/>`_ with a university email address.

.. _api-key:

2. Generate the DACE API key
============================
To obtain an API key:

    1.  Login on DACE (https://dace.unige.ch)
    2.  Go to the user profile
    3.  Click on [Generate a new API key]
    4.  Copy this new API key into the .dacerc file


.. _dacerc:

3. The .dacerc file
===================
The **.dacerc** file, (**you have to create it**), located by default in the home directory (~/.dacerc) and in TOML
format, defines a user section with a key-value pair specifying the user's API key (see below).

.. code-block:: cfg

    [user]
    key = apiKey:<xxx-xxx-xxx>

For example, if your API key is 12345678-1234-5678-1234-567812345678, then the .dacerc file will be :

.. code-block:: cfg

    [user]
    key = apiKey:12345678-1234-5678-1234-567812345678

To create the .dacerc file on Linux or macOs, open a terminal window and type :

.. code-block:: bash

    printf '[user]\nkey = apiKey:%s\n' "your-api-key-here" > ~/.dacerc

Quickstart
**********

.. code-block:: python

    # Import the ready-to-use exoplanet instance
    from dace_query.exoplanet import Exoplanet

    # Retrieve data from the exoplanet database
    result: dict = Exoplanet.query_database(limit=10, output_format='dict')

    # Get the planet names
    planet_names: list = result.get('obj_id_catname')

    # Print the planet names
    print(planet_names)


For more examples of uses, such as **filtering bad quality data** (see Usage examples)

Contact
*******

In case of questions, proposals or problems, feel free to contact the `DACE support <mailto:dace-support@unige.ch>`_ .

Links
*****
* `DACE website <https://dace.unige.ch>`_
