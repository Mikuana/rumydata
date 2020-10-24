"""
Are You My Data (rumydata)

This package provides a set of objects to define a tabular dataset in order to
generate technical specifications for that data, and allow for validation of
a file which claims to adhere to the specification. This eases one of
the main challenges in the transmission of data between parties. The data
definitions are expressive, and highly extensible, allowing for complex rules to
be built into data definitions which can be transmitted via a single, brief
script.

An additional, intentional design choice of this package is that the results of
a validation do everything possible to avoid exposing the contents of a file.
Instead of providing the value that failed validation, the error reporting in
this package provides coordinates (row #, column #), and a detailed explanation
of the rules that were violated. This eases the process of communicating about
data by reducing the chance of disclosing the contents.

There two principles at the core of this package, which greatly simplify the
process of communicating about data by following the don't repeat yourself (DRY)
championed in python.

 1. the code that defines the data, documents the data
 2. the code that defines the data, validates the data

This package attempts to avoid as many dependencies as possible, and can be used
with vanilla python 3.7+. This package is intended to be used on data in text
format (e.g. csv), but can be used to validate Excel spreadsheets by installing
the `openpyxl` package.
"""

from rumydata import field
from rumydata import rules
from rumydata.menu import menu
from rumydata.table import *

__version__ = '0.5.0'
