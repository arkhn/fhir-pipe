import json
from pytest import fixture


@fixture(scope="session")
def exported_source():
    with open("test/data/patient_export.json", "r") as fp:
        return fp.read()


@fixture(scope="session")
def gql_response():
    with open("test/data/patient_gql.json", "r") as fp:
        return json.load(fp)


@fixture(scope="session")
def resource_pruned():
    with open("test/data/patient_pruned.json", "r") as fp:
        return json.load(fp)