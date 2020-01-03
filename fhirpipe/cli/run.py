import time
import numpy as np
import multiprocessing as mp
from functools import partial

from fhirpipe import set_global_config

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.extract.mapping import (
    get_mapping,
    prune_fhir_resource,
    get_identifier_table,
    find_cols_joins_and_scripts,
    build_squash_rules,
)
from fhirpipe.extract.sql import (
    build_sql_query,
    run_sql_query,
)

from fhirpipe.transform.transform import squash_rows, apply_scripts, create_resource

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
        fhirstore.bootstrap(resource=r)

    # Get all resources available in the pyrog mapping for a given source
    resources = get_mapping(from_file=args.mapping, source_name=args.source)
    print("resources: ", [r["name"] for r in resources])

    n_workers = mp.cpu_count()
    pool = mp.Pool(n_workers)

    print(f"Will run for: {args.resources}")

    for resource_structure in resources:
        if args.resources is not None:
            if resource_structure["name"] not in args.resources:
                continue

        print(len(resource_structure["attributes"]))
        resource_structure = prune_fhir_resource(resource_structure)
        print(len(resource_structure["attributes"]))

        # Get main table
        main_table = get_identifier_table(resource_structure)
        print("main_table", main_table)

        # Extract cols and joins
        cols, joins, cleaning, merging = find_cols_joins_and_scripts(resource_structure)

        # Build the sql query
        sql_query = build_sql_query(cols, joins, main_table)
        print(sql_query)

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
            print("Before squash: ", len(chunk))

            # Apply join rule to merge some lines from the same resource
            print("Squashing rows...")
            start = time.time()
            chunk = squash_rows(chunk, squash_rules)
            print("After squash: ", len(chunk))
            print("squash duration: ", time.time() - start)

            # Apply cleaning and merging scripts on chunk
            apply_scripts(chunk, cleaning, merging)

            start = time.time()

            if args.multiprocessing:
                fhir_objects_chunks = pool.map(
                    partial(create_resource, resource_structure=resource_structure),
                    np.array_split(chunk, n_workers),
                )

                print("obj creation duration: ", time.time() - start)

                start = time.time()
                # Save instances in fhirstore
                print("Saving in fhirstore...")
                pool.map(save_many, fhir_objects_chunks)

                print("saving duration: ", time.time() - start)
            else:
                instances = create_resource(chunk, resource_structure)

                save_many(instances)

    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
