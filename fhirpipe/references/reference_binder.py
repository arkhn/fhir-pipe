import re
import logging
from collections import defaultdict

import fhirpipe
from fhirpipe.load.fhirstore import get_mongo_client, get_resource_instances


class ReferenceBinder:
    def __init__(self, fhirstore, skip_ref_binding=False, bypass_validation=False):
        self.fhirstore = fhirstore
        self.skip_ref_binding = skip_ref_binding
        self.bypass_validation = bypass_validation

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
        # {resource_id: [reference_path, ...], ...}
        self.map_resource_references = defaultdict(list)

    def bind_references(self):
        if self.skip_ref_binding:
            return

        for resource_id, reference_paths in self.map_resource_references.items():
            resource_type = self.map_resource_type[resource_id]
            instances_with_refs = get_resource_instances(resource_id, resource_type)
            for instance in instances_with_refs:
                self.bind_references_for_instance(instance, reference_paths)

    def bind_references_for_instance(self, instance, reference_paths):
        patch = {}
        for reference_path in reference_paths:
            try:
                sub_fhir_object = self.bind_reference_for_path(instance, reference_path)
            except Exception as e:
                logging.warning(
                    "Error while binding reference for instance "
                    f"{instance} at path {reference_path}: {e}"
                )

            patch[reference_path] = sub_fhir_object

        self.fhirstore.patch(
            instance["resourceType"],
            instance["id"],
            patch,
            bypass_document_validation=self.bypass_validation,
        )

    def bind_reference_for_path(self, instance, reference_path):
        sub_fhir_object = self.find_sub_fhir_object(instance, reference_path)

        # If we have a list of references, we want to bind all of them.
        # Thus, we loop on all the items in sub_fhir_object.
        if not isinstance(sub_fhir_object, list):
            sub_fhir_object = [sub_fhir_object]

        for sub in sub_fhir_object:
            # Get the map for the needed type
            reference_type = sub["type"]
            map_for_type = self.get_collection_map(reference_type)

            identifier = sub["identifier"]
            key_tuple = self.extract_key_tuple(identifier)

            # If the identifier is in the map, we can fill the reference
            if key_tuple in map_for_type:
                fhir_id = map_for_type[key_tuple]
                sub["reference"] = f"{reference_type}/{fhir_id}"
            else:
                logging.warning(
                    f"Could perform reference binding to the resource of type {reference_type} "
                    f"and identifier {key_tuple}."
                )

        return sub_fhir_object

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
                {"identifier": {"$exists": True}},
                ["id", "identifier.value", "identifier.system", "identifier.type.coding"],
            )

            identifier_map = {}
            for doc in collection:
                for identifier in doc["identifier"]:
                    key_tuple = self.extract_key_tuple(identifier)
                    identifier_map[key_tuple] = doc["id"]

            self.indentifiers_store[fhir_type] = identifier_map

        return self.indentifiers_store[fhir_type]

    def add_reference(self, resource_mapping, path):
        """ When a reference is found, this method stores the useful information about it
        to later perform the binding.
        """
        self.map_resource_type[resource_mapping["id"]] = resource_mapping["definition"]["type"]
        self.map_resource_references[resource_mapping["id"]].append(path)

    def add_references(self, resource_mapping, paths):
        """ When a reference is found, this method stores the useful information about it
        to later perform the binding.
        """
        if self.skip_ref_binding:
            return

        for path in paths:
            self.add_reference(resource_mapping, path)

    @staticmethod
    def find_sub_fhir_object(instance, path):
        cur_sub_object = instance
        for step in path.split("."):
            index = re.search(r"\[(\d+)\]$", step)
            step = re.sub(r"\[\d+\]$", "", step)
            cur_sub_object = cur_sub_object[step]
            if index:
                cur_sub_object = cur_sub_object[int(index.group(1))]

        return cur_sub_object

    @staticmethod
    def extract_key_tuple(identifier):
        """ Build a tuple that contains the essential information from an Identifier.
        This tuple serves as a map key.
        """
        value = identifier["value"]
        # TODO system should have been automatically filled if needed
        system = identifier.get("system")
        identifier_type_coding = identifier["type"]["coding"][0] if "type" in identifier else {}
        identifier_type_system = identifier_type_coding.get("system")
        identifier_type_code = identifier_type_coding.get("code")
        return (value, system, identifier_type_system, identifier_type_code)
