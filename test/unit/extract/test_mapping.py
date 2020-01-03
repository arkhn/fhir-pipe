import pytest
from unittest import mock

import fhirpipe.extract.mapping as mapping


DATA = """
{
    "data": {
        "database": {
            "id": "cjpiarhzxmfmu0a611t9zwqgm",
            "name": "Mimic",
            "resources": [
                {
                    "id": "cjtyglzyd00bh0766w42omeb9",
                    "name": "Patient",
                    "attributes": []
                },
                {
                    "id": "cjtyglzyd00bh0766w42omeb9",
                    "name": "Encounter",
                    "attributes": []
                }
            ]
        }
    }
}
"""

mock_open = mock.mock_open(read_data=DATA)


def test_get_mapping_from_file():
    with mock.patch("builtins.open", mock_open):
        resources = mapping.get_mapping_from_file("path")

    assert [r["name"] for r in resources] == [
        "Patient",
        "Encounter",
    ]


# def test_get_mapping_from_graphql():
#     pass


def test_prune_fhir_resource():
    fhir_resource = {
        "id": "cjtyglzyd00bh0766w42omeb9",
        "name": "Patient",
        "attributes": [
            {
                "id": "cjtyglzz300bi0766tjms54pu",
                "comment": "An identifier for this patient",
                "name": "identifier",
                "mergingScript": None,
                "isProfile": None,
                "type": "list: :Identifier",
                "inputColumns": [],
                "attributes": [],
            },
            {
                "id": "cjtygm07900fy0766v9bkg2lo",
                "comment": "",
                "name": "deceasedDateTime",
                "mergingScript": None,
                "isProfile": None,
                "type": "dateTime",
                "inputColumns": [
                    {
                        "id": "cjtykdfd3045u07661y1d58am",
                        "owner": None,
                        "table": "PATIENTS",
                        "column": "DOD",
                        "script": "format_date_from_yyyymmdd",
                        "staticValue": None,
                        "joins": [],
                    }
                ],
                "attributes": [],
            },
        ],
    }

    expected = {
        "id": "cjtyglzyd00bh0766w42omeb9",
        "name": "Patient",
        "attributes": [
            {
                "id": "cjtygm07900fy0766v9bkg2lo",
                "comment": "",
                "name": "deceasedDateTime",
                "mergingScript": None,
                "isProfile": None,
                "type": "dateTime",
                "inputColumns": [
                    {
                        "id": "cjtykdfd3045u07661y1d58am",
                        "owner": None,
                        "table": "PATIENTS",
                        "column": "DOD",
                        "script": "format_date_from_yyyymmdd",
                        "staticValue": None,
                        "joins": [],
                    }
                ],
                "attributes": [],
            }
        ],
    }

    actual = mapping.prune_fhir_resource(fhir_resource)

    assert actual == expected


def test_find_cols_joins_and_scripts():
    fhir_resource = {
        "id": "cjtyglzyd00bh0766w42omeb9",
        "name": "Patient",
        "attributes": [
            {
                "id": "cjtyglzz300bi0766tjms54pu",
                "comment": "An identifier for this patient",
                "name": "identifier",
                "mergingScript": None,
                "isProfile": None,
                "type": "list: :Identifier",
                "inputColumns": [],
                "attributes": [
                    {
                        "id": "cjtyglzzd00bk076690zuwn0p",
                        "comment": None,
                        "name": "Identifier_0",
                        "mergingScript": None,
                        "isProfile": True,
                        "type": "Identifier",
                        "inputColumns": [],
                        "attributes": [
                            {
                                "id": "cjtygm00x00c807662i1y484t",
                                "comment": "The value that is unique",
                                "name": "value",
                                "mergingScript": None,
                                "isProfile": None,
                                "type": "string",
                                "inputColumns": [
                                    {
                                        "id": "cjtyiyk9500q707661w96ml2j",
                                        "owner": None,
                                        "table": "PATIENTS",
                                        "column": "SUBJECT_ID",
                                        "script": None,
                                        "staticValue": None,
                                        "joins": [],
                                    }
                                ],
                                "attributes": [],
                            }
                        ],
                    }
                ],
            },
            {
                "id": "cjtygm07000fs07660h9zhut2",
                "comment": "male | female | other | unknown",
                "name": "gender",
                "mergingScript": "fake_merging_script",
                "isProfile": None,
                "type": "code",
                "inputColumns": [
                    {
                        "id": "cjtykdszt046607664mzbv9z3",
                        "owner": None,
                        "table": "PATIENTS",
                        "column": "GENDER",
                        "script": "map_gender",
                        "staticValue": None,
                        "joins": [],
                    },
                    {
                        "id": "cjtykdszt046607mzbv9z3",
                        "owner": None,
                        "table": "PATIENTS",
                        "column": "EXPIRE_FLAG",
                        "script": None,
                        "staticValue": None,
                        "joins": [
                            {
                                "id": "cjtykucjh047d0766hopqaa5s",
                                "sourceOwner": None,
                                "sourceTable": "PATIENTS",
                                "sourceColumn": "SUBJECT_ID",
                                "targetOwner": None,
                                "targetTable": "ADMISSIONS",
                                "targetColumn": "SUBJECT_ID",
                            }
                        ],
                    },
                    {
                        "id": "fakeid",
                        "owner": None,
                        "table": None,
                        "column": None,
                        "script": None,
                        "staticValue": "fake static value",
                        "joins": [],
                    },
                ],
                "attributes": [],
            },
        ],
    }

    cols, joins, cleaning, merging = mapping.find_cols_joins_and_scripts(fhir_resource)

    assert cols == {"PATIENTS.SUBJECT_ID", "PATIENTS.EXPIRE_FLAG", "PATIENTS.GENDER"}
    assert joins == {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    assert cleaning == {"map_gender": ["PATIENTS.GENDER"]}
    assert merging == {
        "fake_merging_script": [
            (
                ["map_gender_PATIENTS.GENDER", "PATIENTS.EXPIRE_FLAG"],
                ["fake static value"],
            )
        ]
    }

