from fhirpipe import parse
from fhirpipe import load
from fhirpipe import scripts
from fhirpipe import write

global_config = None


def set_global_config(new_config):
    global global_config
    global_config = new_config
