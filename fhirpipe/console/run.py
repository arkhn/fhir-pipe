import json
import time
import random
import argparse

import fhirpipe
from fhirpipe.console import parse_args
from fhirpipe.console import LIST_RESOURCES

from fhirpipe.console import WELCOME_MSG

from fhirpipe.console.run_resource import run_resource


def run():
    """
    Perform in a single query the processing of all resources and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args("project", "use-graphql-file")

    print(WELCOME_MSG)

    # Launch timer
    start_time = time.time()

    # Define config variables
    project = args.project

    list_resources = LIST_RESOURCES
    n = len(list_resources)

    for i, resource in enumerate(list_resources):
        print(f"Integrating FHIR resource {resource} ({i+1}/{n})")

        main_table = "Patient"

        class Parser:
            """Parameters for the testing"""

            def __init__(self):
                self.project = project
                self.resource = resource
                self.main_table = main_table
                self.use_graphql_file = args.use_graphql_file

        run_resource(from_console=False, args=Parser())

    print(round((time.time() - start_time), 2), "seconds")


def batch_run():
    pass
