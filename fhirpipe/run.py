import time
import logging
import multiprocessing as mp

from fhirstore import NotFoundError
from fhirpipe import set_global_config, setup_logging

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.analyze import Analyzer
from fhirpipe.extract import Extractor
from fhirpipe.transform import Transformer
from fhirpipe.load import Loader

from fhirpipe.analyze.mapping import get_mapping
from fhirpipe.extract.graphql import get_resource_from_id
from fhirpipe.load.fhirstore import get_fhirstore


def run(
    mapping,
    source,
    resources,
    labels,
    override,
    chunksize,
    bypass_validation,
    multiprocessing,
    credentials=None,
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

    pool = None
    if multiprocessing:
        pool = mp.Pool()

    analyzer = Analyzer()
    extractor = Extractor(credentials, chunksize)
    transformer = Transformer(pool)
    loader = Loader(fhirstore, bypass_validation, pool)

    for resource_mapping in resources:
        analysis = analyzer.analyze(resource_mapping)
        df = extractor.extract(resource_mapping, analysis)

        # If the override option is enabled, delete all previous
        # documents matching the resource's mapping id.
        if override:
            try:
                fhirstore.delete(
                    resource_mapping["definition"]["type"], resource_id=resource_mapping["id"]
                )
            except NotFoundError as e:
                logging.warning(f"error while trying to delete previous documents: {e}")

        for chunk in df:
            fhir_instances = transformer.transform(chunk, resource_mapping, analysis)
            loader.load(fhirstore, fhir_instances, resource_mapping["definition"]["type"])

    # TODO we cannot bind references for the moment because we don't have any information about
    # the type of the attributes in the mapping. When this is fixed, we can uncomment what's below
    # (and add something to find the references in the mapping).
    # Now, we can bind the references
    # TODO I think we could find a more efficient way to bind references
    # using more advanced mongo features
    # bind_references(extractor.reference_attributes, identifier_dict, pool)

    if multiprocessing:
        pool.close()
        pool.join()

    logging.info(f"Done in {time.time() - start_time}.")


def preview(resource_id, primary_key_values, credentials):
    """ Run the ETL only for values where the primary key
    """
    # Get the resources we want to process from the pyrog mapping for a given source
    resource_mapping = get_resource_from_id(resource_id=resource_id)

    analyzer = Analyzer()
    extractor = Extractor(credentials)
    transformer = Transformer()

    analysis = analyzer.analyze(resource_mapping)
    df = extractor.extract(resource_mapping, analysis, primary_key_values)
    fhir_instances = transformer.transform(next(df), resource_mapping, analysis)

    return fhir_instances[0]


if __name__ == "__main__":
    print(WELCOME_MSG)

    # Parse arguments
    args = parse_args()

    # Define global config
    set_global_config(config_path=args.config)

    # Setup logging configuration
    setup_logging()

    run(
        mapping=args.mapping,
        source=args.source,
        resources=args.resources,
        labels=args.labels,
        override=args.override,
        chunksize=args.chunksize,
        bypass_validation=args.bypass_validation,
        multiprocessing=args.multiprocessing,
    )
