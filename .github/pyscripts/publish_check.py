import json
import urllib.request
from pathlib import Path

from packaging.version import parse

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

from distutils.version import LooseVersion

pypi_url = f'https://pypi.org/pypi/rumydata/json'
response = urllib.request.urlopen(pypi_url).read().decode()
latest_version = max(LooseVersion(s) for s in json.loads(response)['releases'].keys())
setup_version = json.loads(Path('setup.json').read_text()).get('version')

if parse(setup_version) > parse(str(latest_version)):
    print(f'PASS: version {setup_version} exceeds latest published, {latest_version}')
else:
    raise Exception(f'FAIL: version {setup_version} does not exceed latest published {latest_version}')
