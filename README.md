# Are You My Data?

![img](are-you-my-data.jpg)

[![Documentation Status](https://readthedocs.org/projects/rumydata/badge/?version=latest)](https://rumydata.readthedocs.io/en/latest/?badge=latest)

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
third-party package dependencies. However, if you want to validate the contents
of Microsoft Excel files `.xls`, you will need to install the `openpyxl` package
as well. 

# Alice and Bob Exchange Data

## The Good Way

Let's say Alice wants Bob to send her data. Alice will define her data in a
`Layout`. In the layout, she wants a `Text` field, a `Choice` field, and an
`Integer`.

```python
from rumydata import Layout
from rumydata.field import Text, Integer, Choice

layout = Layout(definition={
    'col1': Text(8),
    'col2': Choice(['x', 'y', 'z']),
    'col3': Integer(1)
})
```

With her layout defined, Alice can now communicate what she wants to Bob. The
`markdown_digest` method outputs a detailed technical specification for the three
fields that Alice included in her definition, in Markdown format.

```python
# ...
layout.markdown_digest()
```

```markdown
 - **col1**
   - Type: String
   - Max Length: 8 characters
   - cannot be empty/blank
   - must be no more than 8 characters
 - **col2**
   - Type: Choice
   - Choices: x,y,z
   - must be one of ['x', 'y', 'z'] (case sensitive)
   - Nullable
 - **col3**
   - Type: Numeric
   - Format: 9
   - Max Length: 1 digits
   - cannot be empty/blank
   - can be coerced into an integer value
   - cannot have a leading zero digit
   - must have no more than 1 digit characters
```

_The code that defines the data, documents the data_. This helps prevent
miscommunication and misunderstanding that occurs when Alice documents separately
from the actual definition of her data.

Bob recieves the documentation, and performs an extract of the requested data
from his system. Bob believes he's followed the documentation exactly as
described, but he's actually made a mistake.

| col1 | col2 | col3 |
|------|------|------|
| abc  | x    | -1   |
| ghi  | a    | 1    |

Bob sends the data to Alice, who then validates it. _The code that defines the
data, validates the data_.

```python
# ...
from rumydata import File

File(layout).check(f'bobs_data.csv')
```

When Alice runs her layout against the csv to check for validity, she receives
the following message:

```yaml
AssertionError: 
 - File: bobs_data.csv
   - Row: 3
     - Cell: 3,2 (col2)
       - InvalidChoice: must be one of ['x', 'y', 'z'] (case sensitive)
```

The second value of the third row does not meet expectations. The message
describes what was expected, and where in the data that expectation was violated.
This error message does **not** describe the value that was provided, which makes
it safe to communicate this error openly. 

Alice sends the message to Bob, and with it he's able to easily see that the 
provided value was not one of the valid choices. Bob can quickly identify the
problem in the data and correct it.

## The Better Way

There's a better way they could have done this. The layout that Alice created
is written in a script that is only seven lines long. That script relies on an
open source, pure-python package, with no hard dependencies. In other words,
the code that defines the data is extremely **portable**.

Instead of sending the techincal documentation (which is even longer than the
script), Alice can instead send Bob the script. With it, Bob can generate the
documentation himself, and validate the data himself, before sending it to
Alice. This skips several rounds of back-and-forth communication in the process. 

# Rules

## Out of the Box

This package contains a number of field types which are already configured with
rules to support that particular type of data. For example, the `Text` field
includes rules for maximum length, minimum length (optional), and nullability.

However, this may not be enough for your purposes. Perhaps you need to ensure
that your text field only includes ASCII characters. Fortunately, a rule for this
already exists in the package, and the Field classes contain a convenient
parameter for applying additional rules to a field.

```python
from rumydata.rules import cell
from rumydata.field import Text

my_field = Text(
    max_length=10, min_length=5, nullable=False, rules=[cell.AsciiChar()]
)

my_field.check_cell('ABCDE')
```

With this new rule applied, any data that is validated against this field will
be checked for minimum and maximum length, nullability, and whether the
characters are all ASCII. You can always test these fields using the
`check_cell` or `check_column` methods, depending up on the
kind of rule that you're trying to test.

## Extension

In the example above, we added a check for ASCII characters only. But what if
we need a rule that doesn't exist in the package? Let's say that we cannot allow
any vowels - A, E, I, O, U - in the cell that we are checking. This package
makes it easy to develop custom rules and apply them to your fields.

```python
from rumydata import field
from rumydata import rules

vowel_rule = rules.cell.make_static_cell_rule(
    lambda x: all([c.lower() not in ['a', 'e', 'i', 'o', 'u'] for c in x]),
    "must not have any vowels"
)

my_field = field.Text(
    max_length=10, min_length=5, nullable=False,
    rules=[rules.cell.AsciiChar(), vowel_rule]
)

my_field.check_cell('ABCDE')
```

With our custom `vowel_rule`, we will now identify any cells that contain values
and call this out during validation.
