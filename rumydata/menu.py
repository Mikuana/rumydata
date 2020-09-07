import webbrowser
from pathlib import Path
from tempfile import TemporaryDirectory

from rumydata.table import Layout


def menu(layout: Layout):
    options = {
        'View Documentation': (_DocGen, dict(ext='html', output='open')),
        'Generate Documentation': (_DocGen, {}),
    }

    print("What would you like to do with this table layout?")
    choice = _select_option(options)[0]
    routine = choice[0](layout, **choice[1])
    return routine.result


class _DocGen:
    def __init__(self, layout: Layout, ext: str = None, output: str = None):
        self.format_options = {'markdown': 'md', 'html': 'html'}
        self.output_options = {
            'print': print,
            'save to file': self.save_doc,
            'open': self.open_browser
        }

        self.layout = layout
        self.ext = ext
        self.output = output
        self.generate_doc()
        self.result = dict(
            completed=True,
            layout=self.layout,
            extension=self.ext,
            output=self.output
        )

    def generate_doc(self):
        output_kwargs = {}

        if not self.ext:
            print("How would you like to format the documentation?")
            self.ext = _select_option(self.format_options)[0]

        if self.ext == 'html':
            try:  # check if markdown to html conversion is available
                import markdown
            except ModuleNotFoundError:  # if not, show markdown directly
                print('markdown module not available; switching to raw md')
                self.ext = 'md'

        documentation = self.layout.documentation(format=self.ext)

        if self.output:
            choice = self.output_options[self.output]
        else:
            print("How would you like to output the documentation?")
            choice, self.output = _select_option(self.output_options)

        if choice is self.open_browser:
            output_kwargs['ext'] = self.ext

        choice(documentation, **output_kwargs)

    @staticmethod
    def save_doc(doc: str):
        ip = input('What path would you like to save the documentation to?\n > ')
        p = Path(ip)
        print(f"Writing to {p.absolute().as_posix()}")
        p.write_text(doc)

    @staticmethod
    def open_browser(doc: str, ext: str):
        with TemporaryDirectory() as td:
            p = Path(td, f'documentation.{ext}')
            p.write_text(doc)
            if p.suffix == '.html':
                webbrowser.open(f'file:///{p.as_posix()}')
            else:
                webbrowser.open(p.as_posix())


def _select_option(options: dict):
    for ix, (k, v) in enumerate(options.items()):
        print(f'[{str(ix)}] {k}')
    choice = input("Choose an option by number or name: ")
    print('')

    try:
        choice = int(choice)
        choice = list(options.keys())[choice]
    except ValueError:
        pass

    return options[choice], choice
