import os

from setuptools import find_packages
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = read("requirements.txt").split()

setup(
    name="fhirpipe",
    version="0.2",
    description="The smart ETL to standardize health data",
    url="https://github.com/arkhn/fhir-pipe",
    author="Théo Ryffel",
    author_email="contact@arkhn.org",
    license="Apache License 2.0",
    packages=find_packages(exclude=["docs", "examples", "dist"]),
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    entry_points={"console_scripts": ["fhirpipe-run=fhirpipe.cli.run:cli_entry_point"]},
)
