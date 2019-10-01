import os

from setuptools import find_packages
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = read("requirements.txt").split()

data_files = [
    'config.yml'
]

setup(
    name='fhirpipe',
    version='0.1',
    description='The smart ETL to standardize health data',
    url='https://github.com/arkhn/fhir-pipe',
    author='Théo Ryffel',
    author_email='contact@arkhn.org',
    license='Apache License 2.0',
    packages=find_packages(exclude=["docs", "examples", "dist"]),
    include_package_data=True,
    data_files=[('', data_files)],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'fhirpipe-run=fhirpipe.console.run:run',
            'fhirpipe-batch-run=fhirpipe.console.run:batch_run',
            'fhirpipe-run-resource=fhirpipe.console.run_resource:run_resource',
            'fhirpipe-batch-run-resource=fhirpipe.console.run_resource:batch_run_resource',
        ],
    },
)
