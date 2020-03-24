from fhirpipe import set_global_config, setup_logging
from fhirpipe.cli import parse_args, WELCOME_MSG
from fhirpipe.run import run


def cli_run():
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
