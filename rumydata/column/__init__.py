from rumydata.column import rule


class Columns:
    def __init__(self, definition: dict, **kwargs):
        """
        Defines the layout of a tabular file.

        :param definition: dictionary of column names with DataType definitions
        """

        self.definition = definition
        self.length = len(definition)
        self.title = kwargs.get('title')

    def digest(self):
        return [[f'Name: {k}', *v.digest()] for k, v in self.definition.items()]

    def markdown_digest(self):
        fields = f'# {self.title}' + '\n\n' if self.title else ''
        fields += '\n'.join([
            f' - **{k}**' + ''.join(['\n   - ' + x for x in v.digest()])
            for k, v in self.definition.items()
        ])
        return fields

    def comparison_columns(self):
        compares = set()
        for v in self.definition.values():
            compares.update(v.comparison_columns())
        return compares
