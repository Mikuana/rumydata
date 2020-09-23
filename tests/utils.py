from unittest.mock import DEFAULT


def mock_no_module(module: str):
    """ force exception on specified module import. For use with mocker """

    def func(*args):
        if args[0] == module:
            raise ModuleNotFoundError
        else:
            return DEFAULT

    return func
