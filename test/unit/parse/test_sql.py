import json
import random
from fhirpipe.parse.sql import get_table_name
from fhirpipe.parse.sql import build_sql_query
from fhirpipe.parse.sql import parse_joins
from fhirpipe.parse.sql import dfs_find_sql_cols_joins
from fhirpipe.parse.sql import find_cols_joins_in_object
from fhirpipe.parse.sql import build_squash_rule

from test.unit.parse import PATIENT_LIGHT_RESOURCE
from test.unit.parse import PATIENT_MEDIUM_RESOURCE


def test_get_table_name():

    full_name = "OWNER.TABLE.COLUMN"
    table = "OWNER.TABLE"

    assert get_table_name(full_name) == table

    full_name = "TABLE.COLUMN"
    table = "TABLE"

    assert get_table_name(full_name) == table


def test_build_sql_query_no_join():
    project = "Crossway"
    resource = json.loads(PATIENT_LIGHT_RESOURCE)
    info = "ICSF.PATIENT"

    sql_query, squash_rules, dependency_graph = build_sql_query(project, resource, info)

    target_sql = (
        "SELECT ICSF.PATIENT.NOPAT, ICSF.PATIENT.NOMPAT, ICSF.PATIENT.PREPAT, "
        "ICSF.PATIENT.PREPATSUITE, ICSF.PATIENT.SEXE FROM ICSF.PATIENT"
    )
    assert target_sql in sql_query

    target_rules = [(0, 1, 2, 3, 4), []]
    assert squash_rules == target_rules


def test_build_sql_query_no_join():
    project = "Crossway"
    resource = json.loads(PATIENT_MEDIUM_RESOURCE)
    info = "ICSF.PATIENT"

    sql_query, squash_rules, dependency_graph = build_sql_query(project, resource, info)

    target_sql1 = (
        "SELECT "
        "ICSF.PATIENT.NOPAT, "
        "ICSF.PATIENT.NOMPAT, "
        "ICSF.PATIENT.PREPAT, "
        "ICSF.PATIENT.PREPATSUITE, "
        "ICSF.PATIENT.SEXE, "
        "ICSF.PATADR.ADR1, "
        "ICSF.PAYS.LIBELLE "
        "FROM ICSF.PATIENT"
    )
    target_sql2 = "LEFT JOIN ICSF.PATADR ON ICSF.PATIENT.NOPAT = ICSF.PATADR.NOPAT"
    target_sql3 = "LEFT JOIN ICSF.PAYS ON ICSF.PATADR.NOPAYS = ICSF.PAYS.NOPAYS"

    assert target_sql1 in sql_query
    assert target_sql2 in sql_query
    assert target_sql3 in sql_query

    target_rules = [
        (0, 1, 2, 3, 4),
        [
            # child 1.1
            [
                (5,),
                [
                    # child 2.1
                    [(6,), []]
                ],
            ]
        ],
    ]

    assert squash_rules == target_rules


def test_parse_joins():
    joins = [
        ("OneToMany", "ICSF.PATIENT.NOPAT=ICSF.PATADR.NOPAT"),
        ("OneToMany", "ICSF.PATADR.NOPAYS=ICSF.PAYS.NOPAYS"),
    ]
    join_elems, graph = parse_joins(joins)

    join_elems_target = [
        ["ICSF.PATADR", "ICSF.PATIENT.NOPAT = ICSF.PATADR.NOPAT"],
        ["ICSF.PAYS", "ICSF.PATADR.NOPAYS = ICSF.PAYS.NOPAYS"],
    ]

    assert join_elems_target == join_elems


def test_dfs_find_sql_cols_joins():
    project = "Crossway"
    resource = json.loads(PATIENT_MEDIUM_RESOURCE)
    info = "ICSF.PATIENT"

    table_name = get_table_name(info + ".*")

    # Get the info about the columns and joins to query
    cols, joins = dfs_find_sql_cols_joins(
        resource, source_table=table_name, project=project
    )

    assert "ICSF.PATIENT.NOPAT" in cols
    assert len(cols) == 7

    assert len(joins) == 2


def test_find_cols_joins_in_object():
    project = "Crossway"
    source_table = "Patient"
    fhir_spec = json.loads(
        """{
                      "id": "cjpicvbl5usn90a57dhmj6m07",
                      "comment": null,
                      "name": "Identifier_0",
                      "mergingScript": null,
                      "isProfile": true,
                      "type": "Identifier",
                      "inputColumns": [

                      ],
                      "attributes": [
                        {
                          "id": "cjpicvbm7usnx0a57f0zp7f4b",
                          "comment": "The value that is unique",
                          "name": "value",
                          "mergingScript": null,
                          "isProfile": null,
                          "type": "string",
                          "inputColumns": [
                            {
                              "id": "cjpil1tdao3lz0a61s50cn8ss",
                              "owner": "ICSF",
                              "table": "PATIENT",
                              "column": "NOPAT",
                              "script": null,
                              "staticValue": null,
                              "joins": [

                              ]
                            }
                          ],
                          "attributes": [

                          ]
                        }
                      ]
                    }"""
    )

    cols, joins = find_cols_joins_in_object(fhir_spec, source_table, project)

    assert cols == ["ICSF.PATIENT.NOPAT"]
    assert joins == []

    fhir_spec = json.loads(PATIENT_MEDIUM_RESOURCE)

    cols, joins = find_cols_joins_in_object(fhir_spec, source_table, project)

    assert cols == [
        "ICSF.PATIENT.NOPAT",
        "ICSF.PATIENT.NOMPAT",
        "ICSF.PATIENT.PREPAT",
        "ICSF.PATIENT.PREPATSUITE",
        "ICSF.PATIENT.SEXE",
        "ICSF.PATADR.ADR1",
        "ICSF.PAYS.LIBELLE",
    ]
    assert len(joins) == 2


def test_build_squash_rule():
    table_name = "ICSF.PATIENT"
    joins = [
        ("OneToMany", "ICSF.PATADR.NOPAYS=ICSF.PAYS.NOPAYS"),
        ("OneToOne", "ICSF.PATIENT.NOPAT=ICSF.FAKE_TABLE.FAKE_COL"),
        ("OneToMany", "ICSF.PATIENT.NOPAT=ICSF.PATADR.NOPAT"),
        ("OneToMany", "ICSF.PATIENT.NOPAT=ICSF.FAKE_TABLE2.FAKE_COL2"),
    ]
    table_col_idx = {
        "ICSF.PATIENT": [0, 1, 2],
        "ICSF.PATADR": [3, 4],
        "ICSF.FAKE_TABLE": [5],
        "ICSF.PAYS": [6],
        "ICSF.FAKE_TABLE2": [7, 8],
    }
    _, graph = parse_joins(joins)
    head_node = graph.get(table_name)
    rules = build_squash_rule(head_node, table_col_idx)

    target_rules = [(0, 1, 2, 5), [[(3, 4), [[(6,), []]]], [(7, 8), []]]]
    assert rules == target_rules
