import argparse


def parse_args():
    """
    Read all the arguments which should describe the run task
    """
    parser = argparse.ArgumentParser(
        description="The smart ETL to standardize health data"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yml",
        help="Path to the configuration file",
    )

    parser.add_argument(
        "-r",
        "--resources",
        nargs="+",
        type=str,
        default=None,
        help="Resource type to process (default: Patient)",
    )

    parser.add_argument(
        "-c",
        "--chunksize",
        type=int,
        default=None,
        help="Batch size if applicable (default: 100000)",
    )

    parser.add_argument(
        "-m",
        "--mapping",
        type=str,
        default=None,
        help="Use graphql file response instead of the API",
    )

    parser.add_argument(
        "-s",
        "--source",
        type=str,
        default="Mimic",
        help="Project to run (default: Mimic)",
    )

    parser.add_argument(
        "--reset_store",
        action="store_true",
        default=False,
        help="Reset fhirstore before writing into it.",
    )

    parser.add_argument(
        "-mp",
        "--multiprocessing",
        action="store_true",
        default=False,
        help="Use multiprocessing to build and save fhir objects.",
    )

    return parser.parse_args()
