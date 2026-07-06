# Are You My Data?

[![PyPI](https://img.shields.io/pypi/v/rumydata)](https://pypi.org/project/rumydata/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rumydata)](https://pypi.org/project/rumydata/)
[![PyPI - License](https://img.shields.io/pypi/l/rumydata)](https://pypi.org/project/rumydata/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rumydata)](https://pypi.org/project/rumydata/)
[![Documentation Status](https://readthedocs.org/projects/rumydata/badge/)](https://rumydata.readthedocs.io/)
[![codecov](https://codecov.io/gh/Mikuana/rumydata/branch/main/graph/badge.svg)](https://codecov.io/gh/Mikuana/rumydata)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SemVer 2.0.0](https://img.shields.io/badge/SemVer-2.0.0-blue)](https://semver.org/spec/v2.0.0.html)

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
 4. sanitized error messages that state what the data *should* be, but not what
    it actually is (i.e., what was expected, not what was received)

# Installation

For most users, the recommended method to install is via pip:

```shell script
pip install rumydata
```

This package requires python version 3.8 or higher. By default, there are no
third-party package dependencies. However, some extras are available.

 - **Excel** `pip install rumydata[Excel]`
 - **Parquet** `pip install rumydata[Parquet]`

# Documentation

Please see the full documentation at [readthedocs](https://rumydata.readthedocs.io/.)
