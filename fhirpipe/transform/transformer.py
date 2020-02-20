import numpy as np
from functools import partial
import logging

from fhirpipe.transform.dataframe import squash_rows, apply_scripts
from fhirpipe.transform.fhir import create_resource


class Transformer:
    def __init__(self, extractor, pool=None):
        self.extractor = extractor
        self.pool = pool

    def transform(self, chunk, resource_structure):
        # Change not string value to strings (to be validated by jsonSchema for resource)
        chunk = chunk.applymap(lambda value: str(value) if value is not None else None)

        # Force names of dataframe cols to be the same as in SQL query
        chunk.columns = self.extractor.cols

        # Apply cleaning and merging scripts on chunk
        apply_scripts(
            chunk,
            self.extractor.cleaning,
            self.extractor.merging,
            self.extractor.primary_key_column,
        )

        # Apply join rule to merge some lines from the same resource
        logging.info("Squashing rows...")
        chunk = squash_rows(chunk, self.extractor.squash_rules)

        if self.pool:
            self.fhir_instances = self.pool.map(
                partial(create_resource, resource_structure=resource_structure),
                np.array_split(chunk, self.pool._processes),
            )
        else:
            self.fhir_instances = create_resource(chunk, resource_structure)
