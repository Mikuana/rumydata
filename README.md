#Are You My Data?

![img](are-you-my-data.jpg)

This is a pure python package which takes on the task of validating the formatting and
contents of data contained in text files (e.g. csv).

 1. examine files completely before raising errors about individual cells
 2. provide ample detail to identify cells, and the kinds of violations that they trigger
 3. protect the privacy of the data in reported error messages


The package allows for the definition of expected file name patterns (using regex),
and a mapping of columns to certain data types which are defined within this package.

```python
from rumydata import *

definitions = [
    DataDefinition(
        r"my_file_\d{8}.csv",
        {
            "ID Number": Text(8),
            "This Name": Text(80),
            "This Choice": Choice(['S', 'N', 'I']),
            "Unit": Choice(['feet', 'inches']),
            "Dollars": Currency(15),
            "Effective Date": Date(),
            "Big Number": Integer(9)
        }
    )
]

File('my_file_20200101.csv', definitions)
```
