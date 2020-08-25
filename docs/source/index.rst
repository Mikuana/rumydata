Are you my data? (rumydata)
===========================

This python package provides a set of tools to solve several of the major challenges
that arise in the transmission of data. These tools attempt to solve four main
problems:

 1. defining exactly what your data should be
 2. communicating that definition to others (so they can send you data)
 3. validating the data that you receive
 4. not disclosing the data on accident

These problems are solved with the following feature sets in this package:

 1. an expressive, extensible set of classes to define a data set
 2. technical documentation generators, based upon the definition
 3. data validation methods, based upon the definition
 4. sanitized error messages which state what the data *should* be, but not what
    it actually is (i.e. what was expected, not what was received)

Installation
############

For most users, the recommended method to install is via pip::

    pip install rumydata

This package requires python version 3.7 or higher. By default there are no
third-party package dependencies. However, if you want to validate the contents
of Microsoft Excel files `.xls`, you will need to install the `openpyxl` package
as well.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   table
   field
   rules
   example


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`