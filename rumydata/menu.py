import webbrowser
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Tuple
from warnings import warn

from rumydata.table import Layout, File

__all__ = ['menu']

_format_options = {'markdown': 'md', 'html': 'html'}


def menu(layout: Layout):
    options = {
        'View Documentation': (_documentation, dict(ext='html', output='open')),
        'Generate Documentation': (_documentation, {}),
        'View Validation': (_validation, dict(ext='html', output='open')),
        'Generate Validation': (_validation, {})
    }

    print("What to do with this layout?")
    choice = _select_option(options)[0]
    return choice[0](layout, **choice[1])


def _documentation(layout: Layout, ext: str = None, output: str = None) -> dict:
    """ Run Layout documentation through menu """
    return _doc_out(*_doc_gen(layout, ext), output)


def _validation(layout: Layout, ext: str = None, output: str = None) -> dict:
    return _doc_out(*_file_check(layout, ext), output)


def _file_check(layout: Layout, ext) -> Tuple[str, str]:
    if not ext:
        print("How to format the documentation?")
        ext = _select_option(_format_options)[0]

    if ext == 'html':
        try:  # check if markdown to html conversion is available
            __import__('markdown')
        except ModuleNotFoundError:
            warn('markdown module not available; falling back to raw md')
            ext = 'md'

    p = input('What is the file path to validate?\n > ')
    errors = File(layout).check(p, doc_type=ext)
    if errors:
        return errors, ext


def _doc_gen(layout: Layout, extension: str = None) -> Tuple[str, str]:
    """ Generate documentation from a layout """

    if not extension:
        print("How to format the documentation?")
        extension = _select_option(_format_options)[0]

    if extension == 'html':
        try:  # check if markdown to html conversion is available
            __import__('markdown')
        except ModuleNotFoundError:
            warn('markdown module not available; falling back to raw md')
            extension = 'md'

    return layout.documentation(doc_type=extension), extension


def _doc_out(document: str, extension: str = None, output: str = None):
    summary = dict(document=document, extension=extension)
    output_options = {'print': print, 'open': _open_doc, 'save': _save_doc}

    if output:
        choice = output_options[output]
    else:
        print("How to output the results?")
        choice, output = _select_option(output_options)

    summary['output'] = output

    output_kwargs = dict(ext=extension) if choice is _open_doc else {}
    choice(document, **output_kwargs)
    return summary


def _save_doc(doc: str):
    ip = input('What path to save the file?\n > ')
    p = Path(ip)
    print(f"Writing to {p.absolute().as_posix()}")
    p.write_text(doc)


def _open_doc(doc: str, ext: str):
    with TemporaryDirectory() as td:
        p = Path(td, f'documentation.{ext}')
        p.write_text(doc)
        if p.suffix == '.html':
            url = f'file:///{p.as_posix()}'
        else:
            url = p.as_posix()
        webbrowser.open(url)
        sleep(0.1)


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
