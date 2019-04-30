import json
import time
import random
import argparse

import fhirpipe
from fhirpipe.console import parse_args


def run_resource(from_console=True, args=None):
    """
    Perform in a single query the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments if needed
    if from_console:
        args = parse_args("project", "resource", "main-table", "use-graphql-file")

    # Launch timer
    start_time = time.time()

    # Define config variables
    project = args.project
    resource = args.resource

    if args.use_graphql_file:
        path = "../../test/integration/fixtures/graphql_mimic_patient.json"
    else:
        path = None

    # Load mapping rules
    resource_structure = fhirpipe.load.graphql.get_fhir_resource(
        project, resource, from_file=path
    )

    # Get main table
    main_table = fhirpipe.parse.fhir.get_identifier_table(resource_structure)

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(
        project, resource_structure, info=main_table
    )

    # Run it
    print("Launching query...")
    rows = fhirpipe.load.sql.run(sql_query)

    print(len(rows), "results")

    # Apply join rule to merge some lines from the same resource
    rows = fhirpipe.load.sql.apply_joins(rows, squash_rules)

    # Build a fhir object for each resource instance
    fhir_objects = []
    for i, row in enumerate(rows):
        if i % 1000 == 0:
            progression = round(i / len(rows) * 100, 2)
            print("Progress... {} %".format(progression))
        row = list(row)
        fhir_object = fhirpipe.parse.fhir.create_fhir_object(
            row, resource, resource_structure
        )
        fhir_objects.append(fhir_object)
        # print(json.dumps(tree, indent=2, ensure_ascii=False))

    # Save instances in fhirbase
    print("Saving in fhirbase...")
    fhirpipe.load.sql.save_in_fhirbase(fhir_objects)

    print(round((time.time() - start_time), 2), "seconds\n")


def batch_run_resource():
    """
    Perform batch by batch the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args(
        "project", "resource", "main-table", "batch-size", "use-graphql-file"
    )

    # Launch timer
    start_time = time.time()

    # Define config variables
    project = args.project
    resource = args.resource
    batch_size = args.batch_size

    # Load data
    resource_structure = fhirpipe.graphql.get_fhir_resource(project, resource)

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(
        project, resource_structure
    )

    # Run it
    print("Launching query batch per batch...")

    offset = fhirpipe.write.log.get("pipe.processing.offset", default=0)

    # Launch the query batch per batch
    for batch_idx, offset, rows in fhirpipe.load.sql.batch_run(
        sql_query, batch_size, offset=offset
    ):
        print("Running batch {} offset {}...".format(batch_idx, offset))
        # Rm None values
        for i, row in enumerate(rows):
            rows[i] = [e if e is not None else "" for e in row]

        # Apply OneToMany joins
        rows = fhirpipe.load.sql.apply_joins(rows, squash_rules)

        # Hydrate FHIR objects
        fhir_objects = []
        for i, row in enumerate(rows):
            if i % 1000 == 0:
                progression = round(i / len(rows) * 100, 2)
                print("batch {} %".format(progression))
            row = list(row)
            fhir_object = fhirpipe.parse.fhir.create_fhir_object(
                row, resource, resource_structure
            )
            fhir_objects.append(fhir_object)

        # Save instances in fhirbase
        print("Saving in fhirbase...")
        fhirpipe.load.sql.save_in_fhirbase(fhir_objects)

        # Log offset to restart in case of a crash
        fhirpipe.write.log.set("pipe.processing.offset", offset)

    # Rm tmp value
    fhirpipe.write.log.rm("pipe.processing.offset")

    print("Done!")

    print(round((time.time() - start_time), 2), "seconds")
