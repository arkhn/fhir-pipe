from pytest import fixture

from fhirpipe.load.fhirstore import get_fhirstore


@fixture(autouse=True)
def reset_store():
    store = get_fhirstore()
    store.reset()
