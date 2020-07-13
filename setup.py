from pathlib import Path

import setuptools

setuptools.setup(
    name="rumydata",
    version="0.0.6",
    author="Christopher Boyd",
    description="A python package for validating expectations of text data, and safely reporting exceptions",
    long_description_content_type="text/markdown",
    url=None,
    long_description=Path('README.md').read_text(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    packages=setuptools.find_packages()
)
