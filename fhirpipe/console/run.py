import json
import time
import random
import argparse

import fhirpipe

# TODO fetch names somewhere
LIST_RESOURCES = ["Patient", "Practitioner"]


def parse_args():
    """
    Read all the arguments which should describe the run task
    """
    parser = argparse.ArgumentParser(description="The smart ETL to standardize health data")
    parser.add_argument(
        "--project",
        type=str,
        default="Mimic",
        help="Project to run (default: Crossway)",
    )
    parser.add_argument(
        "--resource",
        type=str,
        default="Patient",
        choices=set(LIST_RESOURCES),
        help="Resource type to process (default: Patient)",
    )
    parser.add_argument(
        "--main-table",
        type=str,
        default="Patients",
        help="SQL table name (with owner if relevant) of reference for this resource (default: Patients)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default="100000",
        help="Batch size if applicable (default: 100000)",
        required=False,
    )
    parser.add_argument(
        "--use-graphql-file",
        type=bool,
        default=False,
        help="Use graphql file response instead of the API",
        required=False,
    )
    return parser.parse_args()


def run():
    """
    Perform in a single query the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args()

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
    resource_structure = fhirpipe.load.graphql.get_fhir_resource(project, resource, from_file=path)

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(
        project, resource_structure, info=args.main_table
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

    print(round((time.time() - start_time), 2), "seconds")


def batch_run():
    """
    Perform batch by batch the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args()

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
