import json
from pytest import fixture


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
