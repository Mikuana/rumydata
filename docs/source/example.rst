Example
#######

Alice and Bob Exchange Data.

The Good Way
************

Let's say Alice wants Bob to send her data. Alice will define her data in a
`Layout`. In the layout, she wants a `Text` field, a `Choice` field, and an
`Integer`::

    from rumydata import Layout
    from rumydata.field import Text, Integer, Choice

    layout = Layout(definition={
        'col1': Text(8),
        'col2': Choice(['x', 'y', 'z']),
        'col3': Integer(1)
    })

With her layout defined, Alice can now communicate what she wants to Bob. The
`markdown_digest` method outputs a detailed technical specification for the three
fields that Alice included in her definition, in Markdown format::

    # ...
    layout.markdown_digest()

Which generates the output::

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


*The code that defines the data, documents the data*. This helps prevent
miscommunication and misunderstanding that occurs when Alice documents separately
from the actual definition of her data.

Bob receives the documentation, and performs an extract of the requested data
from his system. Bob believes he's followed the documentation exactly as
described, but he's actually made a mistake.



+------+------+------+
| col1 | col2 | col3 |
+======+======+======+
| abc  | x    | -1   |
+------+------+------+
| ghi  | a    | 1    |
+------+------+------+

Bob sends the data to Alice, who then validates it. *The code that defines the
data, validates the data*::

    # ...
    from rumydata import File

    File(layout).check('bobs_data.csv')

When Alice runs her layout against the csv to check for validity, she receives
the following message::

    AssertionError:
     - File: bobs_data.csv
       - Row: 3
         - Cell: 3,2 (col2)
           - InvalidChoice: must be one of ['x', 'y', 'z'] (case sensitive)

The second value of the third row does not meet expectations. The message
describes what was expected, and where in the data that expectation was violated.
This error message does **not** describe the value that was provided, which makes
it safe to communicate this error openly.

Alice sends the message to Bob, and with it he's able to easily see that the
provided value was not one of the valid choices. Bob can quickly identify the
problem in the data and correct it.

The Better Way
**************

There's a better way they could have done this. The layout that Alice created
is written in a script that is only seven lines long. That script relies on an
open source, pure-python package, with no hard dependencies. In other words,
the code that defines the data is extremely **portable**.

Instead of sending the technical documentation (which is even longer than the
script), Alice could instead send Bob the script. With it, Bob can generate the
documentation himself, and validate the data himself, before sending it to
Alice. This skips several rounds of back-and-forth communication in the process

This is made simple through the use of the `menu` function, which takes a layout
object and presents it in a straightforward user interface::

    # alice_validation.py
    from rumydata import Layout, menu
    from rumydata.field import Text, Integer, Choice

    layout = Layout(definition={
        'col1': Text(8),
        'col2': Choice(['x', 'y', 'z']),
        'col3': Integer(1)
    })

    menu(layout)

Assuming that Bob already has python 3.7+ installed, once he receives the script
`alice_validation.py`, all he needs to do is install this package via pip, then
execute this script with the command::

    python alice_validation.py

From there, Bob will be walked through the rest of the documentation generation
and file validation process by the interface.
