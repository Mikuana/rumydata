import webbrowser
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Tuple
from warnings import warn

from rumydata.table import Layout, CsvFile

__all__ = ['menu']

_format_options = {'markdown': 'md', 'html': 'html'}


def menu(layout: Layout) -> dict:
    """
    Layout menu

    This method takes a Layout class object as an argument and presents the user
    with a suite of options in a command line interface (CLI). The options
    include the generation technical documentation for the layout, or validation
    of a csv file, with output of the results.

    Outputs can be printed, saved, or opened (in a web-browser) in either
    markdown or html format, depending upon the user input.

    :param layout: a Layout object which will be used for the selected options.

    :return: a dictionary which describes the results of the interface selection
        choices. Not useful in the wild, but necessary for testing since the
        output is not as easy to verify.
    """
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
    """ Run validation result through menu """
    return _doc_out(*_file_check(layout, ext), output)


def _select_format(ext: str = None) -> str:
    """ Select the output format, falling back to md if markdown is unavailable """
    if not ext:
        print("How to format the documentation?")
        ext = _select_option(_format_options)[0]
    if ext == 'html':
        try:  # check if markdown to html conversion is available
            __import__('markdown')
        except ModuleNotFoundError:
            warn('markdown module not available; falling back to raw md')
            ext = 'md'
    return ext


def _file_check(layout: Layout, ext) -> Tuple[str, str]:
    """ Perform a check of a csv file with (mostly) default params """
    ext = _select_format(ext)

    p = input('What is the file path to validate?\n > ')
    errors = CsvFile(layout).check(p, doc_type=ext)
    if errors:
        return errors, ext
    return None


def _doc_gen(layout: Layout, extension: str = None) -> Tuple[str, str]:
    """ Generate documentation from a layout """
    extension = _select_format(extension)
    return layout.documentation(doc_type=extension), extension


def _doc_out(document: str, extension: str = None, output: str = None):
    """ Output documentation or result """
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
    """ Save str to a specified text file path """
    ip = input('What path to save the file?\n > ')
    p = Path(ip)
    print(f"Writing to {p.absolute().as_posix()}")
    p.write_text(doc)


def _open_doc(doc: str, ext: str):
    """ Open str as a web-browser document """
    with TemporaryDirectory() as td:
        p = Path(td, f'documentation.{ext}')
        p.write_text(doc)
        url = f'file:///{p.as_posix()}' if p.suffix == '.html' else p.as_posix()
        webbrowser.open(url)
        sleep(2)


def _select_option(options: dict):
    """ Present a dictionary of options to the user for selection """
    for ix, k in enumerate(options):
        print(f'[{str(ix)}] {k}')
    choice = input("Choose an option by number or name: ")
    print('')
    try:
        choice = list(options.keys())[int(choice)]  # treat the input as if it was an integer
    except ValueError:  # otherwise assume it was a key value
        pass
    return options[choice], choice
