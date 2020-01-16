import yaml
import logging


with open("config-test.yml", "r") as stream:
    try:
        global_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error(exc)
