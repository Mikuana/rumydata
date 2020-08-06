# Are You My Data?

![img](are-you-my-data.jpg)

This python package takes on the challenges of of transmitting data in text format. 

 1. Provides a simple, and expressive framework to define a data set
 2. Generates explicit documentation on the dataset for communication with others
 3. Validates files against definition, providing detailed messages about violations
    without exposing any information about the actual data in the file


This package provides all of this with the don't repeat yourself (DRY) principle
at its core.

 - the code that defines the data, documents the data
 - the code that defines the data, validates the data


## Example

For this example, we'll pretend that Alice needs Bob to send her data.

Alice will start by defining a layout. In the dataset, she wants a Text column,
a Choice column, and an Integer. She'll define that below, then generate a digest
of the layout so that she can share it with Bob. She accomplishes that with the
code below.

```python

from rumydata.subject import Layout
from rumydata.subject.cell import Text, Integer, Choice
layout = Layout(definition={
    'col1': Text(8),
    'col2': Choice(['x', 'y', 'z'], nullable=True),
    'col3': Integer(1)
})
print(layout.markdown_digest())
```

As you can see in the digest output below, there is a great deal of explicit detail.
This is to the benefit of Bob, who needs to extract data from his source systems
and conform it to Alice's expectations.

This demonstrates a key concept of this package; _the code that defines the data, documents
the data_. This makes Alice's job easier, but also helps to prevent miscommunication
and misunderstanding that occurs when Alice documents the expectation separately
from the actual code.

```markdown
- **col1**
   - Type: String
   - Max Length: 8 characters
   - cannot be empty/blank
   - must be no more than 8 characters
 - **col2**
   - Type: Choice
   - Choices: x,y,z
   - must be one of ['x', 'y', 'z']
   - Nullable
 - **col3**
   - Type: Numeric
   - Format: 9
   - Max Length: 1 digits
   - cannot be empty/blank
   - can be coerced into an integer value
   - cannot have a leading zero digit
   - must have no more than 1 digits after removing other characters
```

In our example, Alice sends the documentation to Bob, who then performs an extract
of the data from his system. Bob thinks he's followed the documentation exactly
as described, but he's actually made a mistake.

| col1 | col2 | col3 |
|------|------|------|
| abc  | x    | -1   |
| def  |      | 0    |
| ghi  | a    | 1    |

Bob sends the data to Alice, who then validates it using her layout. Another key
concept of this package is demonstrated in this step; _the code that defines the
data, validates the data_.

```python

from rumydata.subject import Layout
from rumydata import Choice
from rumydata.subject.cell import Text, Integer
layout = Layout(definition={
    'col1': Text(8),
    'col2': Choice(['x', 'y', 'z'], nullable=True),
    'col3': Integer(1)
})
layout.check_file(f'bobs_data.csv')
```

When Alice checks the file for validity, she receives the following message:

```yaml
AssertionError: 
 - File: None
   - Row: 4
     - Field: 4,2 (col2)
       - InvalidChoice: must be one of ['x', 'y', 'z']
```

The layout has detected that the second value of the fourth row does not meet the
defined expectations, and it has provided a detailed message explaining what was
expected. It is important to note: this error message does **not** describe the
value that was provided, it only describes what was expected, and where in the
data that expectation was violated. This is an intentional design of this package,
as it lets Alice freely communicate with Bob about the issues in the data, with
little risk of exposing the data itself.

Alice sends the message to Bob, and with it he's able to easily see that the value
her provided was not one of the valid choices. He can also refer back to the definition
digest, and see that `col2` is nullable, and that he can send a blank value instead
of the invalid value that he sent.

## Extension

Although this package contains a number of built-in rules to ease the definition
of a `Layout`, it is expected that users will have their own rules that need to
be applied on a regular basis. The simplest way to do this is by generating a
static rule and adding it to a `Field`.

As an example, let's say that Alice realized that the `col3` in her layout needs
to be an *odd* number only. The `Field` class provides a parameter for additional
rules to be specified, and the `make_static_rule` method provides us with a
simple way of generating these rules.

```python
from rumydata import rules, Layout
from rumydata.field import *


odd_rule = rules.cell.make_static_cell_rule(lambda x: int(x) % 2 == 0, "must be an odd number")

layout = Layout(definition={
    'col1': Text(8),
    'col2': Choice(['x', 'y', 'z'], nullable=True),
    'col3': Integer(1, rules=[odd_rule])
})
```

If Alice were to check Bob's data now, it would determine that cell 3,3 is not
an odd number, and raise an exception.
