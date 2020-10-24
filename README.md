# Are You My Data?

[![PyPI](https://img.shields.io/pypi/v/rumydata)](https://pypi.org/project/rumydata/)
[![Documentation Status](https://readthedocs.org/projects/rumydata/badge/)](https://rumydata.readthedocs.io/)
[![codecov](https://codecov.io/gh/Mikuana/rumydata/branch/main/graph/badge.svg)](https://codecov.io/gh/Mikuana/rumydata)

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

# Installation

For most users, the recommended method to install is via pip:

```shell script
pip install rumydata
```

This package requires python version 3.7 or higher. By default there are no
third-party package dependencies. However, some extras are available.

 - **Excel** `pip install rumydata[Excel]`
 - **Parquet** `pip install rumydata[Parquet]`

# Documentation

Please see the full documentation at [readthedocs](https://rumydata.readthedocs.io/.)

# Versioning

This project follows the specifications of [Semantic Versioning 2.0](https://semver.org/).
Users of this package should avoid calling any private or semi-private members
(i.e. starting with one or more underscores `_` in the name). As long as this rule
is followed, upgrading to a higher minor or patch release should always be safe. 
