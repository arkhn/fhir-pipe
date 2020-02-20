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
    build_sql_filters,
    build_sql_query,
    run_sql_query,
    get_connection,
)

from fhirpipe.extract.extractor import Extractor
from fhirpipe.transform.transformer import Transformer
from fhirpipe.load.loader import Loader

from fhirpipe.transform.fhir import create_resource

from fhirpipe.load.fhirstore import get_fhirstore, save_many
from fhirpipe.load.references import build_identifier_dict, bind_references


def run(
    connection,
    mapping,
    source,
    resources,
    labels,
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
    resources = get_mapping(
        from_file=mapping,
        selected_source=source,
        selected_resources=resources,
        selected_labels=labels,
    )

    fhirstore = get_fhirstore()
    if reset_store:
        fhirstore.reset()

    pool = None
    if multiprocessing:
        pool = mp.Pool()

    extractor = Extractor(connection, chunksize)
    transformer = Transformer(extractor, pool)
    loader = Loader(transformer, pool)

    for resource_structure in resources:
        extractor.extract(resource_structure)

        for chunk in extractor.df:
            transformer.transform(chunk)
            loader.load(fhirstore, transformer)

    identifier_dict = build_identifier_dict()

    # Now, we can bind the references
    # TODO I think we could find a more efficient way to bind references
    # using more advanced mongo features
    bind_references(extractor.reference_attributes, identifier_dict, pool)

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
            labels=args.labels,
            reset_store=args.reset_store,
            chunksize=args.chunksize,
            bypass_validation=args.bypass_validation,
            multiprocessing=args.multiprocessing,
            primary_key_values=args.primary_key_values,
        )
