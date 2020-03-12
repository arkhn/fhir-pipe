import re
import logging
from collections import defaultdict

import fhirpipe
from fhirpipe.load.fhirstore import get_mongo_client, get_resource_instances


class ReferenceBinder:
    def __init__(self, fhirstore):
        self.fhirstore = fhirstore
        self.indentifiers_store = {}
        self.map_resource_type = {}
        self.map_resource_references = defaultdict(list)

    def get_collection_map(self, fhir_type):
        if fhir_type not in self.indentifiers_store:
            # TODO don't do this with the mongo client but with fhirstore or API
            db_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]
            collection = db_client[fhir_type].find(
                {"identifier": {"$elemMatch": {"value": {"$exists": True}}}},
                ["id", "identifier.value", "identifier.type"],
            )

            identifier_map = {}
            for doc in collection:
                for identifier in doc["identifier"]:
                    value = identifier["value"]
                    # TODO system should have been automatically filled if needed
                    system = identifier["system"] if "system" in identifier else ""
                    identifier_map[(value, system)] = doc["id"]

            self.indentifiers_store[fhir_type] = identifier_map

        return self.indentifiers_store[fhir_type]

    def bind_references(self):
        for resource_id, references in self.map_resource_references.items():
            resource_type = self.map_resource_type[resource_id]
            instances_with_refs = get_resource_instances(resource_id, resource_type)
            for instance in instances_with_refs:
                self.bind_references_for_instance(instance, resource_type, references)

    def bind_references_for_instance(self, instance, resource_type, references):
        cur_sub_object = instance
        for reference_path, reference_type in references:
            # Go down the fhir object to where the reference is
            for step in reference_path.split("."):
                index = re.search(r"\[(\d+)\]$", step).group(1)
                step = re.sub(r"\[\d+\]$", "", step)
                cur_sub_object = cur_sub_object[step]
                if index:
                    cur_sub_object = cur_sub_object[int(index)]

            map = self.get_collection_map(reference_type)
            identifier = cur_sub_object["identifier"]
            value = identifier["value"]
            # TODO system should have been automatically filled if needed
            system = identifier["system"] if "system" in identifier else ""
            if (value, system) in map:
                cur_sub_object["reference"] = map[(value, system)]
            else:
                # TODO better logging
                logging.log("no bind")

        self.fhirstore.update(resource_type, instance["id"], instance)

    def add_reference(self, resource_mapping, path):
        reference_type = self.find_reference_type(resource_mapping, path)
        self.map_resource_type[resource_mapping["id"]] = resource_mapping["definitionId"]
        self.map_resource_references[resource_mapping["id"]].append((path, reference_type))

    def find_reference_type(self, resource_mapping, path):
        # TODO catch exceptions
        path_type = f"{path}.type"
        type_attribute = next(
            attr for attr in resource_mapping["attributes"] if attr["path"] == path_type
        )
        return type_attribute["inputs"][0]["staticValue"]
