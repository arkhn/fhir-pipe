import time
from tqdm import tqdm

import fhirpipe
from fhirpipe.config import Config
from fhirpipe.console import parse_args
from fhirpipe.load.fhirstore import get_fhirstore


def run_resource(args=None, bootstrap=True):
    """
    Perform in a single query the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments if needed
    if not args:
        args = parse_args()
        fhirpipe.set_global_config(Config(path=args.config))

    # Bootstrap is disabled if console/run_resource is called from console/run
    # Because it is already done there
    if bootstrap:
        fhirstore = get_fhirstore()
        fhirstore.reset()
        fhirstore.bootstrap(depth=5)

    # Launch timer
    start_time = time.time()

    # Load mapping rules
    resource_structure = fhirpipe.load.graphql.get_fhir_resource(
        args.project, args.resource, from_file=args.mock_pyrog_mapping
    )

    # Get main table
    main_table = fhirpipe.parse.fhir.get_identifier_table(resource_structure)

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(
        args.project, resource_structure, info=main_table
    )

    # Run it
    print("Launching query...", flush=True)
    rows = fhirpipe.load.sql.run(sql_query)

    print(len(rows), "results")

    # Apply join rule to merge some lines from the same resource
    rows = fhirpipe.load.sql.apply_joins(rows, squash_rules)

    # Build a fhir object for each resource instance
    fhir_objects = []
    rows = tqdm(rows)
    for i, row in enumerate(rows):
        row = list(row)
        fhir_object = fhirpipe.parse.fhir.create_fhir_object(row, args.resource, resource_structure)
        fhir_objects.append(fhir_object)
        rows.refresh()

    # Save instances in fhirstore
    print("Saving in fhirstore...", flush=True)
    fhirpipe.load.fhirstore.save_many(fhir_objects)

    print(round((time.time() - start_time), 2), "seconds\n", flush=True)


def batch_run_resource():
    """
    Perform batch by batch the processing of a resource and the insertion
    of the fhir data created into the fhir api.

    Note:
        This function can be run from command line
        Some arguments must be provided to set the run task
    """
    # Parse arguments
    args = parse_args()
    fhirpipe.set_global_config(Config(path=args.config))

    # Launch timer
    start_time = time.time()

    # Define config variables
    project = args.project
    resource = args.resource
    batch_size = args.batch_size

    # Load data
    resource_structure = fhirpipe.graphql.get_fhir_resource(
        project, resource, from_file=args.mock_pyrog_mapping
    )

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(project, resource_structure)

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
        rows = tqdm(rows)
        for i, row in enumerate(rows):
            row = list(row)
            fhir_object = fhirpipe.parse.fhir.create_fhir_object(row, resource, resource_structure)
            fhir_objects.append(fhir_object)
            rows.refresh()

        # Save instances in fhirstore
        print("Saving in fhirstore...", flush=True)
        fhirpipe.load.fhirstore.save_many(fhir_objects)

        # Log offset to restart in case of a crash
        fhirpipe.write.log.set("pipe.processing.offset", offset)

    # Rm tmp value
    fhirpipe.write.log.rm("pipe.processing.offset")

    print("Done!")

    print(round((time.time() - start_time), 2), "seconds")
