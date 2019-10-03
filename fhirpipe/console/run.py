import json
import time
import random
import argparse

from fhirpipe import set_global_config
from fhirpipe.config import Config
from fhirpipe.console import parse_args, WELCOME_MSG
from fhirpipe.console.run_resource import run_resource
from fhirpipe.load.graphql import get_available_resources


def run():
    """
    Perform in a single query the processing of all resources and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args()

    print(WELCOME_MSG, flush=True)

    # Launch timer
    start_time = time.time()

    # Define global config
    set_global_config(Config(path=args.config))

    # Get all resources available in the pyrog mapping for a given source
    list_resources = [r["name"] for r in get_available_resources(args.project)]
    n = len(list_resources)

    for i, resource in enumerate(list_resources):
        print(f"Integrating FHIR resource {resource} ({i+1}/{n})")

        main_table = "Patient"

        class Parser:
            """Parameters for the testing"""

            def __init__(self):
                self.resource = resource
                self.main_table = main_table
                self.project = args.project
                self.use_graphql_file = args.use_graphql_file

        run_resource(args=Parser())

    print(round((time.time() - start_time), 2), "seconds")


def batch_run():
    pass
