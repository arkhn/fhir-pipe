import time
import numpy as np
import multiprocessing as mp
from functools import partial

from fhirpipe_clean import set_global_config

from fhirpipe_clean.cli import parse_args, WELCOME_MSG

from fhirpipe_clean.extract.mapping import get_resources, prune_fhir_resource
from fhirpipe_clean.extract.mapping import get_identifier_table
from fhirpipe_clean.extract.sql import find_cols_joins_and_scripts, build_sql_query, build_squash_rules, run_sql_query

from fhirpipe_clean.transform.transform import squash_rows, apply_scripts, create_resource

from fhirpipe_clean.load.fhirstore import get_fhirstore, save_many


def run(selected_resources: list = None):
    """
    """
    # Parse arguments
    args = parse_args()

    print(WELCOME_MSG)

    # Launch timer
    start_time = time.time()

    # Define global config
    set_global_config(config_path=args.config)
    mock_pyrog_mapping = "test/integration/fixtures/graphql_mimic.json"
    selected_resources = ["Patient"]

    # fhirstore = get_fhirstore()
    # fhirstore.reset()
    # fhirstore.bootstrap(depth=5)

    # Get all resources available in the pyrog mapping for a given source
    resources = get_resources(from_file=mock_pyrog_mapping)
    print("resources: ", [r["name"] for r in resources])

    n_workers = mp.cpu_count()
    pool = mp.Pool(n_workers)

    for resource_structure in resources:
        if selected_resources is not None:
            if resource_structure["name"] not in selected_resources:
                continue

        print(len(resource_structure["attributes"]))
        resource_structure = prune_fhir_resource(resource_structure)
        print(len(resource_structure["attributes"]))

        # Get main table
        main_table = get_identifier_table(resource_structure)
        print("main_table", main_table)

        # Extract cols and joins
        cols, joins, cleaning_scripts, merging_scripts = find_cols_joins_and_scripts(resource_structure)
        # Build the sql query
        sql_query = build_sql_query(cols, joins, main_table)
        print(sql_query)

        # Build squash rules
        squash_rules = build_squash_rules(cols, joins, main_table)

        # Run the sql query
        print("Launching query...")
        df = run_sql_query(sql_query)
        df.columns = cols
        print(df)
        print("Before squash: ", len(df))

        # Apply join rule to merge some lines from the same resource
        print("Squashing rows...")
        start = time.time()
        df = squash_rows(df, squash_rules)
        print("After squash: ", len(df))
        print("squash duration: ", time.time() - start)
        print(df)

        # Apply cleaning and merging scripts on df
        apply_scripts(df, cleaning_scripts, merging_scripts)

        start = time.time()

        fhir_objects_chunks = pool.map(
            partial(create_resource, resource_structure=resource_structure),
            np.array_split(df, n_workers)
        )

        for o in fhir_objects_chunks[0][:5]:
            print(o)
        print(len(fhir_objects_chunks[0]))

        print("obj creation duration: ", time.time() - start)

        # start = time.time()
        # Save instances in fhirstore
        # print("Saving in fhirstore...")
        # pool.map(save_many, fhir_objects_chunks)

        # print("saving duration: ", time.time() - start)

    pool.close()
    pool.join()


if __name__ == "__main__":
    run()
