import argparse


def parse_args():
    """
    Read all the arguments which should describe the run task
    """
    parser = argparse.ArgumentParser(description="The smart ETL to standardize health data")

    parser.add_argument(
        "--config", type=str, default="config.yml", help="Path to the configuration file"
    )

    parser.add_argument(
        "--project", type=str, default="Mimic", help="Project to run (default: Mimic)"
    )

    parser.add_argument(
        "--resource",
        type=str,
        default="Patient",
        help="Resource type to process (default: Patient)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default="100000",
        help="Batch size if applicable (default: 100000)",
        required=False,
    )

    parser.add_argument(
        "--main-table",
        type=str,
        default="Patients",
        help="SQL table name (with owner if relevant) of reference\
or this resource (default: Patients)",
    )

    parser.add_argument(
        "--mock-pyrog-mapping",
        type=str,
        default=None,
        help="Use graphql file response instead of the API",
        required=False,
    )
    return parser.parse_args()
