import logging

from fhirpipe.load.fhirstore import save_many


class Loader:
    def __init__(self, fhirstore, bypass_validation):
        self.fhirstore = fhirstore
        self.bypass_validation = bypass_validation

    def load(self, fhirstore, fhir_instances, resource_type):
        logging.info("Loading resource: %s", resource_type)

        # Bootstrap for resource if needed
        if resource_type not in self.fhirstore.resources:
            self.fhirstore.bootstrap(resource=resource_type, depth=3)

        save_many(fhir_instances, self.bypass_validation)
