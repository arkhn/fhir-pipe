import json
from pytest import fixture


@fixture(scope="session")
def exported_source():
    with open("test/fixtures/mimic_mapping.json", "r") as fp:
        return fp.read()


@fixture(scope="session")
def patient_pruned():
    with open("test/fixtures/patient_pruned.json", "r") as fp:
        return json.load(fp)
