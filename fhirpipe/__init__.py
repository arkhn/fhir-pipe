from fhirpipe import parse  # noqa
from fhirpipe import load  # noqa
from fhirpipe import scripts  # noqa
from fhirpipe import write  # noqa

global_config = None


def set_global_config(new_config):
    global global_config
    global_config = new_config
