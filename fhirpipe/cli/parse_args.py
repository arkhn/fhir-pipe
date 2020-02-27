import argparse


def parse_args():
    """
    Read all the arguments which should describe the run task
    """
    parser = argparse.ArgumentParser(description="The smart ETL to standardize health data")

    parser.add_argument(
        "--config", type=str, default="config.yml", help="Path to the configuration file",
    )

    parser.add_argument(
        "-s", "--source", type=str, default=None, help="Name of the source to process",
    )

    parser.add_argument(
        "-r", "--resources", nargs="+", type=str, default=None, help="Resource types to process",
    )

    parser.add_argument(
        "-l", "--labels", nargs="+", type=str, default=None, help="Labels of resources to process",
    )

    parser.add_argument(
        "-c",
        "--chunksize",
        type=int,
        default=None,
        help="Batch size. If None, process the whole DB in one run.",
    )

    parser.add_argument(
        "-m",
        "--mapping",
        type=str,
        default=None,
        help="Use graphql file response instead of the API",
    )

    parser.add_argument(
        "--override",
        action="store_true",
        default=False,
        help="Reset fhirstore before writing into it.",
    )

    parser.add_argument(
        "--skip_ref_binding", action="store_true", default=False, help="Bypass reference binding.",
    )

    parser.add_argument(
        "--bypass_validation",
        action="store_true",
        default=False,
        help="Bypass document validation that should be done by fhirstore.",
    )

    parser.add_argument(
        "-mp",
        "--multiprocessing",
        action="store_true",
        default=False,
        help="Use multiprocessing to build and save fhir objects.",
    )

    parser.add_argument(
        "-pk",
        "--primary_key_values",
        nargs="+",
        type=str,
        default=None,
        help="Row selection from primary key values",
    )

    return parser.parse_args()
