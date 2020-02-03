import time
import logging
import numpy as np
import multiprocessing as mp
from functools import partial
from collections import defaultdict

from fhirpipe import set_global_config, setup_logging

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.extract.mapping import (
    get_mapping,
    prune_fhir_resource,
    get_primary_key,
    find_cols_joins_and_scripts,
    build_squash_rules,
    find_reference_attributes,
)
from fhirpipe.extract.sql import (
    build_sql_query,
    run_sql_query,
    get_connection,
)

from fhirpipe.transform.dataframe import squash_rows, apply_scripts
from fhirpipe.transform.fhir import create_resource

from fhirpipe.load.fhirstore import get_fhirstore, save_many
from fhirpipe.load.references import build_identifier_dict, bind_references


def run(
    connection,
    mapping,
    source,
    resources,
    reset_store,
    chunksize,
    bypass_validation,
    multiprocessing,
):
    """
    """
    # Launch timer
    start_time = time.time()

    # Get the resources we want to process from the pyrog mapping for a given source
    resources = get_mapping(from_file=mapping, source_name=source, selected_resources=resources)

    fhirstore = get_fhirstore()
    if reset_store:
        fhirstore.reset()

    # TODO maybe we can find a more elegant way to handle multiprocessing
    if multiprocessing:
        n_workers = mp.cpu_count()
        pool = mp.Pool(n_workers)

    reference_attributes = defaultdict(set)

    for resource_structure in resources:
        fhirType = resource_structure["fhirType"]

        logging.info("Running for resource: %s", fhirType)
        resource_structure = prune_fhir_resource(resource_structure)

        # Get primary key table
        primary_key_table, primary_key_column = get_primary_key(resource_structure)

        # Extract cols and joins
        cols, joins, cleaning, merging = find_cols_joins_and_scripts(resource_structure)

        # Build the sql query
        sql_query = build_sql_query(cols, joins, primary_key_table)
        logging.info("sql query: %s", sql_query)

        # Build squash rules
        squash_rules = build_squash_rules(cols, joins, primary_key_table)

        # Get all the attributes that are references for future binding
        for attr in find_reference_attributes(resource_structure):
            reference_attributes[fhirType].add(attr)

        # Run the sql query
        logging.info("Launching query...")
        df = run_sql_query(connection, sql_query, chunksize=chunksize)

        for chunk in df:
            # Change not string value to strings (to be validated by jsonSchema for resource)
            chunk = chunk.applymap(lambda value: str(value) if value is not None else None)

            # Force names of dataframe cols to be the same as in SQL query
            chunk.columns = cols

            # Apply cleaning and merging scripts on chunk
            apply_scripts(chunk, cleaning, merging, primary_key_column)

            # Apply join rule to merge some lines from the same resource
            logging.info("Squashing rows...")
            chunk = squash_rows(chunk, squash_rules)

            # Bootstrap for resource if needed
            if fhirType not in fhirstore.resources:
                fhirstore.bootstrap(resource=fhirType, depth=3)

            if multiprocessing:
                fhir_objects_chunks = pool.map(
                    partial(create_resource, resource_structure=resource_structure),
                    np.array_split(chunk, n_workers),
                )

                # Save instances in fhirstore
                pool.map(
                    partial(save_many, bypass_validation=bypass_validation), fhir_objects_chunks,
                )

            else:
                instances = create_resource(chunk, resource_structure)
                save_many(instances, bypass_validation)

    identifier_dict = build_identifier_dict()

    # Now, we can bind the references
    # TODO I think we could find a more efficient way to bind references
    # using more advanced mongo features
    if multiprocessing:
        bind_references(reference_attributes, identifier_dict, pool)
    else:
        bind_references(reference_attributes, identifier_dict)

    if multiprocessing:
        pool.close()
        pool.join()

    logging.info(f"Done in {time.time() - start_time}.")


if __name__ == "__main__":
    print(WELCOME_MSG)

    # Parse arguments
    args = parse_args()

    # Define global config
    set_global_config(config_path=args.config)

    # Setup logging configuration
    setup_logging()

    # Setup DB connection and run
    with get_connection() as connection:
        run(
            connection=connection,
            mapping=args.mapping,
            source=args.source,
            resources=args.resources,
            reset_store=args.reset_store,
            chunksize=args.chunksize,
            bypass_validation=args.bypass_validation,
            multiprocessing=args.multiprocessing,
        )
