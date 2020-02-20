from functools import partial

from fhirpipe.load.fhirstore import get_fhirstore, save_many


class Loader:
    def __init__(self, fhirstore, bypass_validation, extractor, transformer, pool=None):
        self.fhirstore = fhirstore
        self.bypass_validation = bypass_validation
        self.transformer = transformer
        self.pool = pool

    def load(self):
        # Bootstrap for resource if needed
        if self.extractor.fhirType not in self.fhirstore.resources:
            self.fhirstore.bootstrap(resource=self.extractor.fhirType, depth=3)

        if self.pool:
            self.pool.map(
                partial(save_many, bypass_validation=self.bypass_validation),
                self.transformer.fhir_instances,
            )
        else:
            save_many(self.transformer.fhir_instances, self.bypass_validation)
