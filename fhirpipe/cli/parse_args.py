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
        default=100000,
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

    return parser.parse_args()
