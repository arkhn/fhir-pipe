import numpy as np
from functools import partial
import logging

from fhirpipe.transform.dataframe import squash_rows, apply_scripts
from fhirpipe.transform.fhir import create_resource


class Transformer:
    def __init__(self, pool=None):
        self.pool = pool

    def transform(self, chunk, resource_mapping, analysis):
        logging.info("Transforming resource: %s", resource_mapping["definitionId"])

        # Change not string value to strings (to be validated by jsonSchema for resource)
        chunk = chunk.applymap(lambda value: str(value) if value is not None else None)

        # Force names of dataframe cols to be the same as in SQL query
        chunk.columns = [str(col) for col in analysis.cols]

        # Apply cleaning and merging scripts on chunk
        apply_scripts(
            chunk,
            analysis.cleaning_scripts,
            analysis.concept_maps,
            analysis.merging_scripts,
            analysis.primary_key_column,
        )

        # Apply join rule to merge some lines from the same resource
        logging.info("Squashing rows...")
        chunk = squash_rows(chunk, analysis.squash_rules)

        if self.pool:
            fhir_instances = self.pool.map(
                partial(create_resource, resource_mapping=resource_mapping),
                np.array_split(chunk, self.pool._processes),
            )
        else:
            fhir_instances = create_resource(chunk, resource_mapping)

        return fhir_instances
