import pytest
from unittest import mock

from fhirpipe.analyze import Analyzer

import fhirpipe.analyze.mapping as mapping
from fhirpipe.analyze.attribute import Attribute
from fhirpipe.analyze.merging_script import MergingScript
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin

from test.unit.conftest import mock_config, mock_api_get_maps


def test_get_primary_key():
    analyzer = Analyzer()

    # With owner
    resource_mapping = {
        "primaryKeyOwner": "owner",
        "primaryKeyTable": "table",
        "primaryKeyColumn": "col",
    }
    analyzer.get_primary_key(resource_mapping)

    assert analyzer.analysis.primary_key_column == SqlColumn("table", "col", "owner")

    # Without owner
    resource_mapping = {
        "primaryKeyOwner": "",
        "primaryKeyTable": "table",
        "primaryKeyColumn": "col",
    }
    analyzer.get_primary_key(resource_mapping)

    assert analyzer.analysis.primary_key_column == SqlColumn("table", "col")

    # Raising error
    resource_mapping = {
        "primaryKeyOwner": "",
        "primaryKeyTable": "",
        "primaryKeyColumn": "col",
        "definitionId": "fhirtype",
    }
    with pytest.raises(
        ValueError, match="You need to provide a primary key table and column in the mapping"
    ):
        analyzer.get_primary_key(resource_mapping)


@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_analyze_mapping(patient_mapping, fhir_concept_map_gender, fhir_concept_map_identifier):
    analyzer = Analyzer()

    analyzer.analyze_mapping(patient_mapping)

    assert analyzer.analysis.attributes == [
        Attribute(
            "gender",
            columns=[SqlColumn("patients", "gender")],
            static_inputs=["unknown"],
            merging_script=MergingScript("select_first_not_empty"),
        ),
        Attribute(
            "birthDate",
            columns=[SqlColumn("patients", "dob")],
            static_inputs=[],
            merging_script=None,
        ),
        Attribute(
            "maritalStatus.coding[0].code",
            columns=[SqlColumn("admissions", "marital_status")],
            static_inputs=[],
            merging_script=None,
        ),
        Attribute(
            "identifier[0].value",
            columns=[SqlColumn("patients", "row_id")],
            static_inputs=[],
            merging_script=None,
        ),
        Attribute(
            "deceasedBoolean",
            columns=[SqlColumn("patients", "expire_flag")],
            static_inputs=[],
            merging_script=None,
        ),
        Attribute(
            "deceasedDateTime",
            columns=[SqlColumn("patients", "dod")],
            static_inputs=[],
            merging_script=None,
        ),
        Attribute(
            "generalPractitioner[0].type",
            columns=[],
            static_inputs=["/Practitioner/"],
            merging_script=None,
        ),
    ]

    assert analyzer.analysis.columns == {
        SqlColumn("patients", "row_id"),
        SqlColumn("patients", "gender"),
        SqlColumn("patients", "dob"),
        SqlColumn("patients", "dod"),
        SqlColumn("admissions", "marital_status"),
        SqlColumn("patients", "expire_flag"),
    }
    assert analyzer.analysis.joins == {
        SqlJoin(SqlColumn("patients", "subject_id"), SqlColumn("admissions", "subject_id"))
    }
