import json
import random
from fhirpipe.parse.fhir import _is_empty
from fhirpipe.parse.fhir import clean_fhir
from fhirpipe.parse.fhir import dfs_create_fhir_object
from fhirpipe.parse.fhir import create_fhir_object

from test.unit.parse import PATIENT_LIGHT_RESOURCE


def test__is_empty():
    assert _is_empty(None)
    assert _is_empty("NaN")
    assert _is_empty("")
    assert not _is_empty(" ")
    assert not _is_empty("arkhn")
    assert not _is_empty(24)


def test_clean_fhir():
    dirty_tree = []
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == []

    dirty_tree = {}
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == {}

    dirty_tree = [
        {'a': 1}
    ]
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == dirty_tree

    dirty_tree = [
        {'a': 1},
        {}
    ]
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == [
        {'a': 1}
    ]

    dirty_tree = [
        {'a': 1},
        []
    ]
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == [
        {'a': 1}
    ]

    dirty_tree = [
        {'a': 1},
        [{}, [[], {}]]
    ]
    cleaned_tree, _ = clean_fhir(dirty_tree)
    assert cleaned_tree == [
        {'a': 1}
    ]


def test_dfs_create_fhir_object():
    fhir_spec = json.loads("""{
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
                }""")
    fhir_obj = dict()
    dfs_create_fhir_object(fhir_obj, fhir_spec, ['1009283'])

    assert fhir_obj == {'value': '1009283'}


    fhir_spec = json.loads("""{
              "id": "cjpicvbmouso90a57p8irnpx6",
              "comment": "A name associated with the patient",
              "name": "name",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::HumanName",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbmrusob0a57ru95njt5",
                  "comment": null,
                  "name": "HumanName_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "HumanName",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvbmuusod0a572zcixgqn",
                      "comment": "usual | official | temp | nickname | anonymous | old | maiden",
                      "name": "use",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "code",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbmyusoh0a579qvwoi1p",
                      "comment": "Family name (often called 'Surname')",
                      "name": "family",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpikp174o1ia0a61owy0aumv",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "NOMPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbn1usoj0a57209fc3np",
                      "comment": "Given names (not always 'first'). Includes middle names",
                      "name": "given",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "list::string",
                      "inputColumns": [
                        {
                          "id": "cjpikpcxeo1k70a61o2qeklnj",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        },
                        {
                          "id": "cjpikpfl6wji10a57cyj19385",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPATSUITE",
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
                }
              ]
            }""")

    fhir_obj = dict()
    dfs_create_fhir_object(fhir_obj, fhir_spec, ['Chirac', 'Jacques', 'François'])

    assert fhir_obj == {'name': [{'family': 'Chirac', 'given': ['Jacques', 'François'], 'use': {}}]}

    clean_fhir_obj, n_leafs = clean_fhir(fhir_obj)

    assert clean_fhir_obj == {'name': [{'family': 'Chirac', 'given': ['Jacques', 'François']}]}

    assert n_leafs == 3

def test_create_fhir_object():
    row = ['100092', 'Chirac', 'Jacques', 'François', 'M']
    resource = "Patient"
    resource_patient_structure = json.loads(PATIENT_LIGHT_RESOURCE)
    fhir_object = create_fhir_object(row, resource, resource_patient_structure)
    fhir_id = fhir_object['id']
    assert fhir_object == {
        'id': fhir_id,
        'resourceType': 'Patient',
        'identifier': [{'value': '100092'}],
        'name': [{'family': 'Chirac',
                  'given': ['Jacques', 'François']}],
        'gender': 'M'
    }

