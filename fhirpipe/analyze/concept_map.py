from typing import TypeVar
import requests
import numpy as np
import logging

import fhirpipe
from fhirpipe.errors import OperationOutcome

T = TypeVar("T", bound="ConceptMap")


class ConceptMap:
    def __init__(
        self, concept_map_id: str,
    ):
        """
        Converts a FHIR concept map to an object which is easier to use.
        """
        fhir_concept_map = ConceptMap.fetch(concept_map_id)

        self.mapping = ConceptMap.convert_to_dict(fhir_concept_map)
        self.id = fhir_concept_map["id"]
        self.title = fhir_concept_map["title"]

    def __eq__(self, operand: T) -> bool:
        return self.title == operand.title and self.mapping == operand.mapping

    @staticmethod
    def fetch(concept_map_id: str) -> T:
        api_url = fhirpipe.global_config["fhir-api"]["url"]
        try:
            response = requests.get(f"{api_url}/ConceptMap/{concept_map_id}")
        except requests.exceptions.ConnectionError as e:
            raise OperationOutcome(f"Could not connect to the fhir-api service: {e}")

        if response.status_code != 200:
            raise Exception(f"Error while fetching concept map {concept_map_id}: {response.text}.")
        return response.json()

    @staticmethod
    def convert_to_dict(fhir_concept_map):
        mapping = {}
        for group in fhir_concept_map["group"]:
            for element in group["element"]:
                # NOTE fhirpipe can only handle a single target for each source
                source_code = element["code"]
                target_code = element["target"][0]["code"]
                mapping[source_code] = target_code
        return mapping

    def translate(self, source_code: str) -> str:
        return self.mapping[source_code]

    def apply(self, df_column, pk_column):
        def map_and_log(val, id=None, col=None):
            try:
                return self.translate(val)
            except Exception as e:
                logging.error(f"{self.title}: Error mapping {col} (at id = {id}): {e}")

        return np.vectorize(map_and_log)(df_column, id=pk_column, col=df_column.name[0])
