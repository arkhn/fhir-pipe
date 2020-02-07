from fhirpipe import set_global_config, setup_logging
from fhirpipe.cli import parse_args, WELCOME_MSG
from fhirpipe.extract.sql import get_connection
from fhirpipe.run import run


def cli_run():
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
            sources=args.source,
            resources=args.resources,
            labels=args.labels,
            reset_store=args.reset_store,
            chunksize=args.chunksize,
            bypass_validation=args.bypass_validation,
            multiprocessing=args.multiprocessing,
        )
