import argparse


# TODO fetch names somewhere
LIST_RESOURCES = [
    "Patient",
    "Practitioner",
    "Encounter",
    "MedicationRequest",
    "Procedure",
]


def parse_args(*args):
    """
    Read all the arguments which should describe the run task
    """
    parser = argparse.ArgumentParser(
        description="The smart ETL to standardize health data"
    )

    if "project" in args:
        parser.add_argument(
            "--project",
            type=str,
            default="Mimic",
            help="Project to run (default: Crossway)",
        )

    if "resource" in args:
        parser.add_argument(
            "--resource",
            type=str,
            default="Patient",
            choices=set(LIST_RESOURCES),
            help="Resource type to process (default: Patient)",
        )

    if "main-table" in args:
        parser.add_argument(
            "--main-table",
            type=str,
            default="Patients",
            help="SQL table name (with owner if relevant) of reference for this resource (default: Patients)",
        )

    if "batch-size" in args:
        parser.add_argument(
            "--batch-size",
            type=int,
            default="100000",
            help="Batch size if applicable (default: 100000)",
            required=False,
        )

    if "use-graphql-file" in args:
        parser.add_argument(
            "--use-graphql-file",
            type=bool,
            default=False,
            help="Use graphql file response instead of the API",
            required=False,
        )
    return parser.parse_args()
