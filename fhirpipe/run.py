import time
import logging
import multiprocessing as mp
from jsonschema.exceptions import ValidationError

from fhirstore import NotFoundError
from fhirpipe import set_global_config, setup_logging

from fhirpipe.cli import parse_args, WELCOME_MSG

from fhirpipe.analyze import Analyzer
from fhirpipe.extract import Extractor
from fhirpipe.transform import Transformer
from fhirpipe.load import Loader
from fhirpipe.references import ReferenceBinder

from fhirpipe.analyze.mapping import get_mapping
from fhirpipe.extract.graphql import get_resource_from_id
from fhirpipe.load.fhirstore import get_fhirstore


def run(
    mapping,
    resource_ids,
    override,
    chunksize,
    bypass_validation,
    skip_ref_binding,
    multiprocessing,
    credentials=None,
):
    """
    """
    # Launch timer
    start_time = time.time()

    # Get the resources we want to process from the pyrog mapping for a given source
    resources = get_mapping(from_file=mapping, resource_ids=resource_ids)

    fhirstore = get_fhirstore()

    pool = None
    if multiprocessing:
        pool = mp.Pool()

    analyzer = Analyzer()
    extractor = Extractor(credentials, chunksize)
    transformer = Transformer(pool)
    loader = Loader(fhirstore, bypass_validation, pool)

    # TODO is there a more elegant way to skip_ref_binding?
    binder = ReferenceBinder(fhirstore, skip_ref_binding)

    for resource_mapping in resources:
        # Analyze
        analysis = analyzer.analyze(resource_mapping)

        # Add references to map if any
        binder.add_references(resource_mapping, analysis.reference_paths)

        # Extract
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
            # Transform
            fhir_instances = transformer.transform(chunk, resource_mapping, analysis)
            # Load
            loader.load(fhirstore, fhir_instances, resource_mapping["definition"]["type"])

    binder.bind_references()

    if multiprocessing:
        pool.close()
        pool.join()

    logging.info(f"Done in {time.time() - start_time}.")


def preview(resource_id, primary_key_values, credentials):
    """ Run the ETL only for values where the primary key
    """
    # The fhirstore will be used to validate resource instances
    fhirstore = get_fhirstore()

    # Get the resources we want to process from the pyrog mapping for a given source
    resource_mapping = get_resource_from_id(resource_id=resource_id)

    analyzer = Analyzer()
    extractor = Extractor(credentials)
    transformer = Transformer()

    analysis = analyzer.analyze(resource_mapping)
    df = extractor.extract(resource_mapping, analysis, primary_key_values)
    fhir_instances = transformer.transform(next(df), resource_mapping, analysis)

    # Execute validation
    errors = []
    for fhir_instance in fhir_instances:
        try:
            fhirstore.validate(fhir_instance)
        except ValidationError as e:
            errors.append(str(e))

    return fhir_instances, errors


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
        resource_ids=args.resource_ids,
        override=args.override,
        chunksize=args.chunksize,
        bypass_validation=args.bypass_validation,
        skip_ref_binding=args.skip_ref_binding,
        multiprocessing=args.multiprocessing,
    )
