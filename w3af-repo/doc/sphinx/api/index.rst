REST API Introduction
=====================

This documentation section is a user guide for w3af's REST API service, its goal
is to provide developers the knowledge to consume w3af as a service using any
development language.

We recommend you read through the `w3af users guide <http://docs.w3af.org/>`_
before diving into this REST API-specific section.

Starting the REST API service
-----------------------------

.. code-block:: none

    $ ./w3af_api
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

REST API Source code
--------------------

The `REST API <https://github.com/andresriancho/w3af/tree/master/w3af/core/ui/api/>`_
is implemented in Flask and is pretty well documented for your reading pleasure.

Contents
--------

.. toctree::
   :maxdepth: 2

   scans
   kb
