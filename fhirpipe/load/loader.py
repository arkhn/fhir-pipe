from functools import partial
import logging

from fhirpipe.load.fhirstore import save_many


class Loader:
    def __init__(self, fhirstore, bypass_validation, pool=None):
        self.fhirstore = fhirstore
        self.bypass_validation = bypass_validation
        self.pool = pool

    def load(self, fhirstore, fhir_instances, resource_type):
        logging.info("Loading resource: %s", resource_type)

        # Bootstrap for resource if needed
        if resource_type not in self.fhirstore.resources:
            self.fhirstore.bootstrap(resource=resource_type, depth=3)

        if self.pool:
            self.pool.map(
                partial(save_many, bypass_validation=self.bypass_validation, multi_processing=True),
                fhir_instances,
            )
        else:
            save_many(fhir_instances, self.bypass_validation)
