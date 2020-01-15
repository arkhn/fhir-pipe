import time
import numpy as np
import multiprocessing as mp
from functools import partial

from pymongo.errors import CollectionInvalid

from fhirpipe import set_global_config

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.extract.mapping import (
    get_mapping,
    prune_fhir_resource,
    get_main_table,
    find_cols_joins_and_scripts,
    build_squash_rules,
)
from fhirpipe.extract.sql import (
    build_sql_query,
    run_sql_query,
)

from fhirpipe.transform.dataframe import squash_rows, apply_scripts
from fhirpipe.transform.fhir import create_resource

from fhirpipe.load.fhirstore import get_fhirstore, save_many


def run():
    """
    """
    # Parse arguments
    args = parse_args()

    print(WELCOME_MSG)

    # Launch timer
    start_time = time.time()

    # Define global config
    set_global_config(config_path=args.config)

    fhirstore = get_fhirstore()
    if args.reset_store:
        fhirstore.reset()
    for r in args.resources:
        try:
            fhirstore.bootstrap(resource=r, depth=10)
        except CollectionInvalid:
            fhirstore.resume()

    # Get the resources we want to process from the pyrog mapping for a given source
    resources = get_mapping(
        from_file=args.mapping,
        source_name=args.source,
        selected_resources=args.resources,
    )

    # TODO maybe we can find a more elegant way to handle multiprocessing
    if args.multiprocessing:
        n_workers = mp.cpu_count()
        pool = mp.Pool(n_workers)

    print(f"Will run for: {args.resources}")
    for resource_structure in resources:
        print("Running for resource:", resource_structure["fhirType"])
        resource_structure = prune_fhir_resource(resource_structure)

        # Get main table
        main_table = get_main_table(resource_structure)
        print("main_table", main_table)

        # Extract cols and joins
        cols, joins, cleaning, merging = find_cols_joins_and_scripts(resource_structure)

        # Build the sql query
        sql_query = build_sql_query(cols, joins, main_table)
        print("sql query:", sql_query)

        # Build squash rules
        squash_rules = build_squash_rules(cols, joins, main_table)

        # Run the sql query
        print("Launching query...")
        df = run_sql_query(sql_query, chunksize=args.chunksize)

        for chunk in df:
            # Change not string value to strings (to be validated by jsonSchema for resource)
            chunk = chunk.applymap(str)

            # Force names of dataframe cols to be the same as in SQL query
            chunk.columns = cols

            # Apply join rule to merge some lines from the same resource
            print("Squashing rows...")
            chunk = squash_rows(chunk, squash_rules)

            # Apply cleaning and merging scripts on chunk
            apply_scripts(chunk, cleaning, merging)

            if args.multiprocessing:
                fhir_objects_chunks = pool.map(
                    partial(create_resource, resource_structure=resource_structure),
                    np.array_split(chunk, n_workers),
                )

                # Save instances in fhirstore
                pool.map(save_many, fhir_objects_chunks)

            else:
                instances = create_resource(chunk, resource_structure)
                save_many(instances)

    if args.multiprocessing:
        pool.close()
        pool.join()

    print(f"Done in {time.time() - start_time}.")


if __name__ == "__main__":
    run()
