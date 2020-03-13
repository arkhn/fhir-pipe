import re
import logging
from collections import defaultdict

import fhirpipe
from fhirpipe.load.fhirstore import get_mongo_client, get_resource_instances


class ReferenceBinder:
    def __init__(self, fhirstore):
        self.fhirstore = fhirstore

        # store of the form
        # {
        #   fhir_type: {(value, system): fhir_id, ...},
        #   fhir_type: {(value, system): fhir_id, ...},
        #   ...
        # }
        self.indentifiers_store = {}

        # map from resource_id to resource type
        self.map_resource_type = {}

        # map_resource_references is a dict of the form
        # {resource_id: [(reference_path, reference_type), ...], ...}
        self.map_resource_references = defaultdict(list)

    def get_collection_map(self, fhir_type):
        """ Get a dict {(value, system): fhir_id, ...} for the specified resource type.
        If the type is in identifiers_store, we simply return self.indentifiers_store[fhir_type].
        Else, we fetch all the resources in the store having an identifier
        and fill the store before.
        """
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
        for reference_path, reference_type in references:
            sub_fhir_object = self.find_sub_fhir_object(instance, reference_path)
            identifier = sub_fhir_object["identifier"]

            # Get the map for the needed type
            map = self.get_collection_map(reference_type)
            value = identifier["value"]
            # TODO system should have been automatically filled if needed
            system = identifier["system"] if "system" in identifier else ""

            # If the identifier is in the map, we can fill the reference
            if (value, system) in map:
                sub_fhir_object["reference"] = map[(value, system)]
            else:
                logging.warn(
                    f"Could perform reference binding to the resource of type {reference_type} "
                    f"and identifier {(value, system)}."
                )

        self.fhirstore.update(resource_type, instance["id"], instance)

    def add_reference(self, resource_mapping, path):
        """ When a reference is found, this method stores the useful information about it
        to later perform the binding.
        """
        reference_type = self.find_reference_type(resource_mapping, path)
        self.map_resource_type[resource_mapping["id"]] = resource_mapping["definitionId"]
        self.map_resource_references[resource_mapping["id"]].append((path, reference_type))

    def find_reference_type(self, resource_mapping, path):
        """ Get the type of the referenced fhir resource from a mapping and the path
        of the reference attribute.
        """
        path_type = f"{path}.type"
        try:
            type_attribute = next(
                attr for attr in resource_mapping["attributes"] if attr["path"] == path_type
            )
        except IndexError:
            logging.error("Trying to find the reference type at a path which doesn't exist.")

        if (
            "inputs" not in type_attribute
            or len(type_attribute["inputs"]) > 1
            or "staticValue" not in type_attribute["inputs"][0]
        ):
            logging.error("Trying to find the reference type for an attribute poorly formatted.")

        return type_attribute["inputs"][0]["staticValue"]

    @staticmethod
    def find_sub_fhir_object(instance, path):
        cur_sub_object = instance
        for step in path.split("."):
            index = re.search(r"\[(\d+)\]$", step).group(1)
            step = re.sub(r"\[\d+\]$", "", step)
            cur_sub_object = cur_sub_object[step]
            if index:
                cur_sub_object = cur_sub_object[int(index)]

        return cur_sub_object
