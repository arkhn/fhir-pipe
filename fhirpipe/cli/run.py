import time
import numpy as np
import multiprocessing as mp
from functools import partial
from collections import defaultdict

from fhirpipe import set_global_config

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.extract.mapping import (
    get_mapping,
    prune_fhir_resource,
    get_main_table,
    find_cols_joins_and_scripts,
    build_squash_rules,
    find_reference_attributes,
)
from fhirpipe.extract.sql import build_sql_query, run_sql_query

from fhirpipe.transform.dataframe import squash_rows, apply_scripts
from fhirpipe.transform.fhir import create_resource

from fhirpipe.load.fhirstore import get_fhirstore, save_many
from fhirpipe.load.references import build_identifier_dict, bind_references


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

    # Get the resources we want to process from the pyrog mapping for a given source
    resources = get_mapping(
        from_file=args.mapping,
        source_name=args.source,
        selected_resources=args.resources,
    )

    fhirstore = get_fhirstore()
    if args.reset_store:
        fhirstore.reset()

    # TODO maybe we can find a more elegant way to handle multiprocessing
    if args.multiprocessing:
        n_workers = mp.cpu_count()
        pool = mp.Pool(n_workers)

    reference_attributes = defaultdict(set)

    for resource_structure in resources:
        fhirType = resource_structure["fhirType"]

        print("Running for resource:", fhirType)
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

        # Get all the attributes that are references for future binding
        for attr in find_reference_attributes(resource_structure):
            reference_attributes[fhirType].add(attr)

        # Run the sql query
        print("Launching query...")
        df = run_sql_query(sql_query, chunksize=args.chunksize)

        for chunk in df:
            # Change not string value to strings (to be validated by jsonSchema for resource)
            chunk = chunk.applymap(str)

            # Force names of dataframe cols to be the same as in SQL query
            chunk.columns = cols

            # Apply cleaning and merging scripts on chunk
            apply_scripts(chunk, cleaning, merging)

            # Apply join rule to merge some lines from the same resource
            print("Squashing rows...")
            chunk = squash_rows(chunk, squash_rules)

            # Bootstrap for resource if needed
            if fhirType not in fhirstore.resources:
                fhirstore.bootstrap(resource=fhirType, depth=10)

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

    identifier_dict = build_identifier_dict()

    # Now, we can bind the references
    # TODO I think we could find a more efficient way to bind references
    # using more advanced mongo features
    if args.multiprocessing:
        bind_references(reference_attributes, identifier_dict, pool)
    else:
        bind_references(reference_attributes, identifier_dict)

    if args.multiprocessing:
        pool.close()
        pool.join()

    print(f"Done in {time.time() - start_time}.")


if __name__ == "__main__":
    run()
