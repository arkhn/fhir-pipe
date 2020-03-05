import json
from pytest import fixture

cm_code = {
    "group": [
        {
            "element": [
                {"code": "ABCcleaned", "target": [{"code": "abc"}]},
                {"code": "DEFcleaned", "target": [{"code": "def"}]},
                {"code": "GHIcleaned", "target": [{"code": "ghi"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm_code",
    "id": "id_cm_code",
}

cm_gender = {
    "group": [
        {
            "element": [
                {"code": "M", "target": [{"code": "male"}]},
                {"code": "F", "target": [{"code": "female"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm_gender",
    "id": "id_cm_gender",
}

cm_identifier = {
    "group": [
        {
            "element": [
                {"code": "1", "target": [{"code": "A"}]},
                {"code": "2", "target": [{"code": "B"}]},
                {"code": "3", "target": [{"code": "C"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm_identifier",
    "id": "id_cm_identifier",
}


@fixture(scope="session")
def fhir_concept_map_code():
    return cm_code


@fixture(scope="session")
def fhir_concept_map_identifier():
    return cm_identifier


@fixture(scope="session")
def fhir_concept_map_gender():
    return cm_gender


def mock_api_get_maps(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, text):
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    if args[0] == "https://url/api/ConceptMap/id_cm_code":
        return MockResponse(cm_code, 200, "")
    elif args[0] == "https://url/api/ConceptMap/id_cm_gender":
        return MockResponse(cm_gender, 200, "")
    elif args[0] == "https://url/api/ConceptMap/id_cm_identifier":
        return MockResponse(cm_identifier, 200, "")
    return MockResponse(None, 404, "not found")


@fixture(scope="session")
def exported_source():
    with open("test/fixtures/mimic_mapping.json", "r") as fp:
        return fp.read()


@fixture(scope="session")
def patient_mapping():
    with open("test/fixtures/patient_mapping.json", "r") as fp:
        return json.load(fp)


mock_config = {
    "fhirstore": {"database": "fhirstore"},
    "graphql": {"token": "gql_token", "server": "gql_server"},
    "sql": {
        "default": "postgres",
        "postgres": {
            "args": ["postgres_arg1", "postgres_arg2"],
            "kwargs": {"kwarg1": "postgres_kwarg1", "kwarg2": "postgres_kwarg2"},
        },
        "oracle": {
            "args": ["oracle_arg1", "oracle_arg2"],
            "kwargs": {"kwarg1": "oracle_kwarg1", "kwarg2": "oracle_kwarg2"},
        },
    },
    "fhir-api": {"url": "https://url/api"},
}
