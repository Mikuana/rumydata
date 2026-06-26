import json
import re
import urllib.request
from pathlib import Path

from packaging.version import Version, parse

try:
    from importlib.metadata import version
except ImportError:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    pass



def read_version():
    try:
        v = [x for x in Path('rumydata/__init__.py').open() if x.startswith('__version__')][0]
        v = re.match(r"__version__ *= *'(.*?)'\n", v)[1]
        return v
    except Exception as e:
        raise RuntimeError(f"Unable to read version string: {e}")


pypi_url = 'https://pypi.org/pypi/rumydata/json'
response = urllib.request.urlopen(pypi_url).read().decode()
releases = json.loads(response)['releases'].keys()
latest_version = max(Version(s) for s in releases)
setup_version = read_version()

if parse(setup_version) > parse(str(latest_version)):
    print(f'PASS: version {setup_version} exceeds latest published, {latest_version}')
else:
    raise Exception(f'FAIL: version {setup_version} does not exceed latest published {latest_version}')
