import yaml
import logging
import fhirpipe


with open("config-test.yml", "r") as stream:
    try:
        fhirpipe.global_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error(exc)
