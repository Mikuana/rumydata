import webbrowser
from pathlib import Path
from tempfile import TemporaryDirectory

from rumydata.table import Layout


def menu(layout: Layout):
    options = {
        'View Documentation': (
            _generate_doc, dict(ext='html', output='open in browser')
        ),
        'Generate Documentation': (_generate_doc, {}),
        'Validate File': (_validate_file, {})
    }

    print("What would you like to do with this table layout?")
    choice = _select_option(options)
    choice[0](layout, **choice[1])


def _generate_doc(layout: Layout, ext: str = None, output: str = None):
    doc_kwargs = {}
    format_options = {'markdown': 'md', 'html': 'html'}
    if ext:
        doc_kwargs['format'] = ext
    else:
        print("How would you like to format the documentation?")
        doc_kwargs['format'] = _select_option(format_options)

    documentation = layout.documentation(**doc_kwargs)

    output_options = {'print': _print_doc, 'save to file': _save_doc}
    if doc_kwargs['format'] == 'html':
        output_options['open in browser'] = _open_browser

    if output:
        choice = output_options[output]
    else:
        print("How would you like to output the documentation?")
        choice = _select_option(output_options)
    choice(documentation)


def _print_doc(doc: str):
    print(doc)


def _save_doc(doc: str):
    ip = input('What path would you like to save the documentation to?\n > ')
    p = Path(ip)
    print(f"Writing to {p.absolute().as_posix()}")
    p.write_text(doc)


def _open_browser(doc: str):
    with TemporaryDirectory() as td:
        p = Path(td, 'documentation.html')
        p.write_text(doc)
        webbrowser.open_new_tab(f'file:///{p.as_posix()}')


def _validate_file():
    pass


def _select_option(options: dict):
    for ix, (k, v) in enumerate(options.items()):
        print(f'[{str(ix)}] {k}')
    choice = int(input("Choose an option (by number): "))
    print('')
    return list(options.values())[choice]


if __name__ == '__main__':
    from rumydata.field import Integer

    menu(Layout({'col1': Integer(1)}))
