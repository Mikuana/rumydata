import re
from pathlib import Path

import setuptools


def read_version():
    try:
        v = [x for x in Path('rumydata/__init__.py').open() if x.startswith('__version__')][0]
        v = re.match(r"__version__ *= *'(.*?)'\n", v)[1]
        return v
    except Exception as e:
        raise RuntimeError(f"Unable to read version string: {e}")


setuptools.setup(
    name="rumydata",
    version=read_version(),
    author="Christopher Boyd",
    description="A python package for validating expectations of text data, and safely reporting exceptions",
    long_description_content_type="text/markdown",
    url="https://github.com/Mikuana/rumydata",
    long_description=Path('README.md').read_text(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    extras_require={
        'Excel': ['openpyxl'],
        'Parquet': ['pandas', 'pyarrow'],
        'HTML': ['markdown'],
        'Testing': [
            'pytest', 'pytest-mock', 'pytest-cov', 'openpyxl', 'markdown',
            'pandas', 'pyarrow'
        ]
    },
    packages=setuptools.find_packages()
)
