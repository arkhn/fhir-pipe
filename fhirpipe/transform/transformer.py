import numpy as np
from multiprocessing import Manager
from functools import partial
import logging

from fhirpipe.transform.dataframe import clean_dataframe, squash_rows, merge_dataframe
from fhirpipe.transform.fhir import create_resource, create_static_instance


class Transformer:
    def __init__(self, pool=None):
        self.pool = pool

    def transform(self, chunk, resource_mapping, analysis):
        logging.info("Transforming resource: %s", resource_mapping["definitionId"])

        # Change not string value to strings (to be validated by jsonSchema for resource)
        chunk = chunk.applymap(lambda value: str(value) if value is not None else None)

        # Apply cleaning scripts and concept map on chunk
        chunk = clean_dataframe(chunk, analysis.attributes, analysis.primary_key_column)

        # We need to remove None values because pandas removes rows with
        # these on groupby
        chunk.replace(to_replace=[None], value="None", inplace=True)

        # Apply join rule to merge some lines from the same resource
        logging.info("Squashing rows...")
        chunk = squash_rows(chunk, analysis.squash_rules)

        # Put None values back
        chunk.replace(to_replace={"None": None}, inplace=True)

        # Apply merging scripts on chunk
        chunk = merge_dataframe(chunk, analysis.attributes, analysis.primary_key_column)

        if self.pool:
            fhir_instances = Manager().list()
            self.pool.map(
                partial(
                    create_resource,
                    resource_mapping=resource_mapping,
                    attributes=analysis.attributes,
                    res=fhir_instances,
                ),
                np.array_split(chunk, self.pool._processes),
            )
        else:
            fhir_instances = []
            create_resource(chunk, resource_mapping, analysis.attributes, fhir_instances)

        return fhir_instances

    def transform_static_resource(self, resource_mapping, analysis):
        return create_static_instance(resource_mapping, analysis.attributes)
