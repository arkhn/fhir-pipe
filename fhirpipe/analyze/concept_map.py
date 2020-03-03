from typing import TypeVar
import requests
import pandas as pd
import numpy as np
import logging

import fhirpipe
from fhirpipe.errors import OperationOutcome

T = TypeVar("T", bound="ConceptMap")


class ConceptMap:
    def __init__(
        self, fhir_concept_map: dict,
    ):
        """
        Converts a FHIR concept map to an object which is easier to use.
        """
        self.title = fhir_concept_map["title"]
        self.columns = []
        self.mapping = {}
        for group in fhir_concept_map["group"]:
            for element in group["element"]:
                # NOTE fhirpipe can only handle a single target for each source
                source_code = element["code"]
                target_code = element["target"][0]["code"]
                self.mapping[source_code] = target_code

    def __eq__(self, operand: T) -> bool:
        return (
            self.title == operand.title
            and self.mapping == operand.mapping
            and self.columns == operand.columns
        )

    @staticmethod
    def fetch(concept_map_id: str) -> T:
        api_url = fhirpipe.global_config["fhir-api"]["url"]
        try:
            response = requests.get(f"{api_url}/ConceptMap/{concept_map_id}")
        except requests.exceptions.ConnectionError as e:
            raise OperationOutcome(f"Could not connect to the fhir-api service: {e}")

        if response.status_code != 200:
            raise Exception(
                f"Error while fetching concept map {concept_map_id}: {response.json()}."
            )
        return ConceptMap(response.json())

    def get(self, source_code: str) -> str:
        return self.mapping[source_code]

    def apply(self, df: pd.DataFrame, pk_column: str):
        def map_and_log(val, id=None, col=None):
            try:
                return self.get(val)
            except Exception as e:
                logging.error(f"{self.title}: Error mapping {col} (at id = {id}): {e}")

        for col in self.columns:
            yield col, np.vectorize(map_and_log)(df[col], id=df[pk_column], col=col)
