Rules
=====

.. automodule:: rumydata.rules

Out of the Box
##############

This package contains a number of field types which are already configured with
rules to support that particular type of data. For example, the `Text` field
includes rules for maximum length, minimum length (optional), and nullability.

However, this may not be enough for your purposes. Perhaps you need to ensure
that your text field only includes ASCII characters. Fortunately, a rule for this
already exists in the package, and the Field classes contain a convenient
parameter for applying additional rules to a field::

    from rumydata.rules import cell
    from rumydata.field import Text

    my_field = Text(
        max_length=10, min_length=5, nullable=False, rules=[cell.AsciiChar()]
    )

    my_field.check_cell('ABCDE')

With this new rule applied, any data that is validated against this field will
be checked for minimum and maximum length, nullability, and whether the
characters are all ASCII. You can always test these fields using the
`check_cell` or `check_column` methods, depending up on the kind of rule that
you're trying to test.

Extension
#########

In the example above, we added a check for ASCII characters only. But what if
we need a rule that doesn't exist in the package? Let's say that we cannot allow
any vowels - A, E, I, O, U - in the cell that we are checking. This package
makes it easy to develop custom rules and apply them to your fields::

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

With our custom `vowel_rule`, we will now identify any cells that contain values
and call this out during validation.

Reference
#########

Cell
****

.. automodule:: rumydata.rules.cell
    :members:
    :show-inheritance:

Column
******

.. automodule:: rumydata.rules.column
    :members:
    :show-inheritance:
