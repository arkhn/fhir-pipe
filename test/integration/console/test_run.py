import datetime

import fhirpipe


def test_adapted_run():
    """
    We run first all the element of the run functions but in local mode
    """

    # Define config variables
    project = "Mimic"
    resource = "Patient"

    # Load LOCAL mapping rules
    path = "../../test/integration/fixtures/graphql_mimic_patient.json"
    resource_structure = fhirpipe.load.graphql.get_fhir_resource(
        project, resource, from_file=path
    )

    # Build the sql query
    sql_query, squash_rules, graph = fhirpipe.parse.sql.build_sql_query(
        project, resource_structure, info="PATIENTS"
    )

    # Run it
    print("Launching query...")
    rows = fhirpipe.load.sql.run(sql_query)

    # Fix: replace None values with '' AND replace date with str representation
    for i, row in enumerate(rows):
        new_row = []
        for el in row:
            if el is None:
                new_row.append("")
            elif isinstance(el, datetime.datetime):
                new_row.append(str(el))
            else:
                new_row.append(el)
        rows[i] = new_row

    print(len(rows), "results")

    # Apply join rule to merge some lines from the same resource
    rows = fhirpipe.load.sql.apply_joins(rows, squash_rules)

    # Build a fhir object for each resource instance
    fhir_objects = []
    for i, row in enumerate(rows):
        if i % 3000 == 0:
            progression = round(i / len(rows) * 100, 2)
            print("Progress... {} %".format(progression))
        row = list(row)
        fhir_object = fhirpipe.parse.fhir.create_fhir_object(
            row, resource, resource_structure
        )
        fhir_objects.append(fhir_object)
        # print(json.dumps(tree, indent=2, ensure_ascii=False))
