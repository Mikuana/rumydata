"""
data validation rules

This submodule contains the various rules that are used to validate the contents
of a file, to determine if it meets the specifications of a layout.

The rules are divided by the various types:
 - cell: the most basic rule type. A cell rule generally receives a single
   value, but can also perform comparison to other value that exist in the same
   row.
 - column: a more complex rule type which requires knowledge of the entire
   list of values present in a single column in order to determine validity.
 - row: rules that are applied to an entire row. These are not generally meant
   to be extended by users of this package.
 - header: rules that extend the concept of row rules, but are meant to apply
   specifically to the header row of the file.
 - file: rules that apply to the file, including whether the file exists, or
   matches a particular naming convention.
"""

from rumydata.rules import cell, column, row, header, table

__all__ = ['cell', 'column', 'row', 'header', 'table']
