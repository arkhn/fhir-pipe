import fhirpipe


def test_get_fhir_resource():
    path = "test/integration/fixtures/graphql_mimic_patient.json"
    resource_structure = fhirpipe.load.graphql.get_fhir_resource(
        "Mimic", "Patient", from_file=path
    )

    assert any(
        attr["name"] == "identifier"
        for attr in resource_structure["attributes"]
    )
